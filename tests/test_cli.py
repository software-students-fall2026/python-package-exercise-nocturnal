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
    outputs = list((working_directory / "pynesthesia" / "jingles").glob("*.mp3"))

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
    directory = working_directory / "pynesthesia" / "jingles"
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
        ["html"],
        ["html", "relative.txt"]
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

def test_html_from_file(working_directory, capsys):
    """Check that a file creates an html page"""
    file = working_directory / "html_test.txt"
    file.write_bytes(b"hello")
    cli.main(["html", str(file)])
    outputs = list(
        (working_directory / "pynesthesia" / "fortunes").glob("*.html")
    )

    assert len(outputs) == 1
    assert outputs[0].stat().st_size > 0
    assert len(outputs[0].stem) == 12
    assert str(outputs[0]) in capsys.readouterr().out

    page = outputs[0].read_text(encoding="utf-8")

    assert "Yesterday's Fortune" in page
    assert "Today's Fortune" in page
    assert "Tomorrow's Fortune" in page

def test_html_is_repeatable(working_directory):
    """Check that the same input file gives the same html page"""
    file = working_directory / "html_test.txt"
    file.write_bytes(b"hello")
    cli.main(["html", str(file)])
    directory = working_directory / "pynesthesia" / "fortunes"
    output = next(directory.glob("*.html"))
    first_page = output.read_bytes()

    cli.main(["html", str(file)])

    assert list(directory.glob("*.html")) == [output]
    assert output.read_bytes() == first_page

def test_different_files_make_different_html_names(working_directory):
    """Check that different files get different output names"""
    first_file = working_directory / "first.txt"
    second_file = working_directory / "second.txt"
    first_file.write_bytes(b"hello")
    second_file.write_bytes(b"goodbye")

    cli.main(["html", str(first_file)])
    cli.main(["html", str(second_file)])

    outputs = list(
        (working_directory / "pynesthesia" / "fortunes").glob("*.html")
    )

    assert len(outputs) == 2
    assert outputs[0].name != outputs[1].name

def test_html_with_missing_file(working_directory, capsys):
    """Check that a missing file creates no fortune page."""
    cli.main(["html", str(working_directory / "missing_file.txt")])

    assert "Error processing file" in capsys.readouterr().out
    assert not (working_directory / "pynesthesia").exists()


def test_cli_colorizes(capsys):
    """check that colorize prints colored text"""
    cli.main(["--colorize", "0f"])

    assert capsys.readouterr().out.strip() == colors.colorize("0f")
