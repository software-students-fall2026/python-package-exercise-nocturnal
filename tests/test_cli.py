import os
import subprocess
import sys
from pathlib import Path

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


def test_cli_requires_a_path(capsys):
    """simulate missing file path"""
    # argparse exits when the required path is missing
    with pytest.raises(SystemExit) as exc:
        cli.main(["jingle"])

    # argparse uses exit code 2 for invalid arguments
    assert exc.value.code == 2
    assert "path" in capsys.readouterr().err


def test_jingle_from_file(working_directory, capsys):
    """check that a file creates a jingle"""
    file = working_directory / "input.txt"
    file.write_bytes(b"hello")
    output = working_directory / "jingle.mid"

    cli.main(["jingle", str(file)])

    assert output.exists()
    assert str(output) in capsys.readouterr().out


def test_jingle_with_missing_file(working_directory, capsys):
    """check that a missing file does not create a jingle"""
    cli.main(["jingle", str(working_directory / "missing.txt")])

    assert "Error processing file" in capsys.readouterr().out
    assert not (working_directory / "jingle.mid").exists()


def test_jingle_does_not_replace_file(working_directory, capsys):
    """check that an existing jingle is not replaced"""
    file = working_directory / "input.txt"
    file.write_bytes(b"hello")
    output = working_directory / "jingle.mid"
    output.write_bytes(b"existing")

    # argparse exits when the output already exists
    with pytest.raises(SystemExit) as exc:
        cli.main(["jingle", str(file)])

    # argparse uses exit code 2 and the original file stays unchanged
    assert exc.value.code == 2
    assert "already exists" in capsys.readouterr().err
    assert output.read_bytes() == b"existing"


def test_relative_path(capsys):
    """check that a relative path shows an error"""
    # argparse uses exit code 2 for invalid input
    with pytest.raises(SystemExit) as exc:
        cli.main(["jingle", "relative.txt"])

    assert exc.value.code == 2
    assert "absolute file path" in capsys.readouterr().err


def test_cannot_save_jingle(working_directory, capsys):
    """check that a save error is reported"""
    file = working_directory / "input.txt"
    file.write_bytes(b"hello")

    # remove the current directory so the file cannot be saved
    directory = working_directory / "removed"
    directory.mkdir()
    os.chdir(directory)
    directory.rmdir()

    with pytest.raises(SystemExit) as exc:
        cli.main(["jingle", str(file)])

    # argparse uses exit code 2 when it reports an error
    assert exc.value.code == 2
    assert "could not save jingle" in capsys.readouterr().err


def test_module_creates_jingle(tmp_path):
    """check that the command creates a jingle"""
    file = tmp_path / "random.txt"
    file.write_bytes(b"random text file")

    # run the command in a temporary directory
    result = subprocess.run(
        [sys.executable, "-m", "pynesthesia", "jingle", str(file)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    output = tmp_path / "jingle.mid"

    # exit code 0 means the command ran successfully
    assert result.returncode == 0
    assert output.exists()
    assert str(output) in result.stdout
