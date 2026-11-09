import hashlib
import os
import subprocess
import sys
from pathlib import Path

import mido
import pytest

import pynesthesia.cli as cli


@pytest.fixture
def working_directory(tmp_path):
    # move into a temporary directory so the jingle is saved there
    previous = Path.cwd()
    os.chdir(tmp_path)
    yield tmp_path

    # return to the original directory after the test
    os.chdir(previous)


def test_cli_prints_file_hash(tmp_path, capsys):
    """simulate hashing a text file"""
    file = tmp_path / "random.txt"
    random_bytes = b"random text file"

    file.write_bytes(random_bytes)
    expected_output = hashlib.sha256(random_bytes).hexdigest()

    cli.hash_file(str(file))
    assert capsys.readouterr().out.strip() == expected_output


def test_cli_with_missing_file(tmp_path, capsys):
    """simulate file not found error condition"""
    filepath = tmp_path / "missing.txt"

    cli.hash_file(str(filepath))
    assert "Error processing file" in capsys.readouterr().out


def test_cli_requires_a_path(capsys):
    """simulate missing file path"""
    # argparse exits when the required path is missing
    with pytest.raises(SystemExit) as exc:
        cli.main([])

    # argparse uses exit code 2 for invalid arguments
    assert exc.value.code == 2
    assert "path" in capsys.readouterr().err


def test_module_entry_point(tmp_path):
    """simulate running the package"""
    file = tmp_path / "random.txt"
    random_bytes = b"random text file"

    file.write_bytes(random_bytes)
    expected_output = hashlib.sha256(random_bytes).hexdigest()
    result = subprocess.run(
        [sys.executable, "-m", "pynesthesia", str(file)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == expected_output


def test_jingle_from_file_and_seed(working_directory, capsys):
    """check that a file and its hash make the same jingle"""
    file = working_directory / "input.txt"
    file.write_bytes(b"hello")
    seed = hashlib.sha256(b"hello").hexdigest()
    output = working_directory / "jingle.mid"

    # create a jingle from the file
    cli.main(["--file", str(file)])
    first = output.read_bytes()

    # read the midi messages and count the notes
    notes = [
        message for message in mido.MidiFile(output).tracks[0]
        if message.type == "note_on"
    ]

    assert str(output) in capsys.readouterr().out
    assert len(notes) == 32

    # remove the first file so the next command can save another
    output.unlink()
    cli.main(["--seed", seed])

    assert output.read_bytes() == first
    assert str(output) in capsys.readouterr().out


def test_jingle_with_missing_file(working_directory, capsys):
    """check that a missing file does not create a jingle"""
    cli.main(["--file", str(working_directory / "missing.txt")])

    assert "Error processing file" in capsys.readouterr().out
    assert not (working_directory / "jingle.mid").exists()


def test_jingle_does_not_replace_file(working_directory, capsys):
    """check that an existing jingle is not replaced"""
    output = working_directory / "jingle.mid"
    output.write_bytes(b"existing")

    # argparse exits when the output already exists
    with pytest.raises(SystemExit) as exc:
        cli.main(["--seed", "00" * 32])

    # argparse uses exit code 2 and the original file stays unchanged
    assert exc.value.code == 2
    assert "already exists" in capsys.readouterr().err
    assert output.read_bytes() == b"existing"


@pytest.mark.parametrize("args, message", [
    (["--seed", "invalid"], "valid sha-256 hash"),
    (["--file", "relative.txt"], "absolute file path"),
    (["relative.txt"], "absolute file path"),
    (["/some/file", "--seed", "00" * 32], "provide one file path"),
])
def test_invalid_arguments(args, message, capsys):
    """check that invalid inputs show an error"""
    # argparse exits when the input is invalid
    with pytest.raises(SystemExit) as exc:
        cli.main(args)

    # argparse uses exit code 2 for invalid arguments
    assert exc.value.code == 2
    assert message in capsys.readouterr().err


def test_cannot_save_jingle(working_directory, capsys):
    """check that a save error is reported"""
    # remove the current directory so the file cannot be saved
    directory = working_directory / "removed"
    directory.mkdir()
    os.chdir(directory)
    directory.rmdir()

    with pytest.raises(SystemExit) as exc:
        cli.main(["--seed", "00" * 32])

    # argparse uses exit code 2 when it reports an error
    assert exc.value.code == 2
    assert "could not save jingle" in capsys.readouterr().err


def test_module_creates_jingle(tmp_path):
    """check that the command creates a jingle"""
    file = tmp_path / "random.txt"
    file.write_bytes(b"random text file")

    # run the command in a temporary directory
    result = subprocess.run(
        [sys.executable, "-m", "pynesthesia", "--file", str(file)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    output = tmp_path / "jingle.mid"

    # exit code 0 means the command ran successfully
    assert result.returncode == 0
    assert output.exists()
    assert str(output) in result.stdout
