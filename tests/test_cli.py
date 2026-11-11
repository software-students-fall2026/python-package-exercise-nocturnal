import os
from pathlib import Path

import pytest

import pynesthesia.cli as cli
import pynesthesia.colors as colors


@pytest.fixture
def working_directory(tmp_path):
    """save jingles in a temporary directory"""
    previous_directory = Path.cwd()
    os.chdir(tmp_path)
    yield tmp_path

    # return to the original directory
    os.chdir(previous_directory)


def test_jingle_from_file(working_directory, capsys):
    """check that a file creates a jingle"""
    file = working_directory / "little_file_bro.txt"
    file.write_bytes(b"hello")
    cli.main(["jingle", str(file), "--measures", "1"])
    outputs = list((working_directory / "jingles").glob("*.mp3"))

    assert len(outputs) == 1
    assert outputs[0].stat().st_size > 0
    assert "_measures-1.mp3" in outputs[0].name
    assert str(outputs[0]) in capsys.readouterr().out


def test_jingle_is_repeatable(working_directory):
    """check that the same file makes the same mp3"""
    file = working_directory / "same_file_bro.txt"
    file.write_bytes(b"hello")
    options = ["--measures", "1"]
    cli.main(["jingle", str(file), *options])
    directory = working_directory / "jingles"
    output = next(directory.glob("*.mp3"))
    first_audio = output.read_bytes()

    cli.main(["jingle", str(file), *options])

    assert list(directory.glob("*.mp3")) == [output]
    assert output.read_bytes() == first_audio


def test_jingle_with_missing_file(working_directory, capsys):
    """check that a missing file creates no jingle"""
    cli.main(["jingle", str(working_directory / "missing_file_bro.txt")])

    assert "Error processing file" in capsys.readouterr().out
    assert not (working_directory / "pynesthesia").exists()


def test_invalid_commands(tmp_path):
    """check that invalid commands are rejected"""
    file = str(tmp_path / "input.txt")
    commands = [
        [], ["jingle"], ["jingle", "relative.txt"],
        ["jingle", file, "--measures", "0"],
        ["jingle", file, "--measures", "113"],
        ["--colorize", "0f", "jingle", file],
    ]
    for command in commands:
        # argparse uses exit code 2 for errors
        with pytest.raises(SystemExit) as error:
            cli.main(command)

        assert error.value.code == 2


def test_cannot_save_jingle(working_directory, capsys):
    """check that a save error is reported"""
    file = working_directory / "input.txt"
    file.write_bytes(b"hello")

    # remove the current directory first
    # this prevents saving the output
    directory = working_directory / "removed"
    directory.mkdir()
    os.chdir(directory)
    directory.rmdir()

    with pytest.raises(SystemExit) as error:
        cli.main(["jingle", str(file)])

    assert error.value.code == 2
    assert "could not save jingle" in capsys.readouterr().err


def test_cli_colorizes(capsys):
    """check that colorize prints colored text"""
    cli.main(["--colorize", "0f"])

    assert capsys.readouterr().out.strip() == colors.colorize("0f")
