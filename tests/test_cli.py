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
    outputs = list((working_directory / "pynesthesia_output" / "jingles").glob("*.mp3"))

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
    directory = working_directory / "pynesthesia_output" / "jingles"
    output = next(directory.glob("*.mp3"))
    first_audio = output.read_bytes()

    cli.main(["jingle", str(file), *options])

    assert list(directory.glob("*.mp3")) == [output]
    assert output.read_bytes() == first_audio


def test_jingle_with_missing_file(working_directory, capsys):
    """check that a missing file creates no jingle"""
    cli.main(["jingle", str(working_directory / "missing_file_bro.txt")])

    assert "Error processing file" in capsys.readouterr().out
    assert not (working_directory / "pynesthesia_output").exists()


def test_invalid_commands(tmp_path):
    """check that invalid commands are rejected"""
    file = str(tmp_path / "input.txt")
    commands = [
        [], ["jingle"], ["jingle", "relative.txt"],
        ["jingle", file, "--measures", "0"],
        ["jingle", file, "--measures", "113"],
        ["colorize"],
        ["html"],
        ["html", "relative.txt"],
        ["flower"],
        ["flower", "relative.txt"]
    ]
    for command in commands:
        # argparse uses exit code 2 for errors
        with pytest.raises(SystemExit) as error:
            cli.main(command)

        assert error.value.code == 2


def test_cannot_save_jingle(working_directory, capsys, monkeypatch):
    """check that a save error is reported"""
    file = working_directory / "input.txt"
    file.write_bytes(b"hello")

    # Simulate save error without changing the working directory
    def fail_save(*args, **kwargs):
        raise OSError("permission denied")
    monkeypatch.setattr(cli.output_writer, "save_mp3", fail_save)

    with pytest.raises(SystemExit) as error:
        cli.main(["jingle", str(file)])

    assert error.value.code == 2
    assert "could not save output" in capsys.readouterr().err

def test_html_from_file(working_directory, capsys):
    """Check that a file creates an html page"""
    file = working_directory / "html_test.txt"
    file.write_bytes(b"hello")
    cli.main(["html", str(file)])
    outputs = list(
        (working_directory / "pynesthesia_output" / "fortunes").glob("*.html")
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
    directory = working_directory / "pynesthesia_output" / "fortunes"
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
        (working_directory / "pynesthesia_output" / "fortunes").glob("*.html")
    )

    assert len(outputs) == 2
    assert outputs[0].name != outputs[1].name

def test_html_with_missing_file(working_directory, capsys):
    """Check that a missing file creates no fortune page."""
    cli.main(["html", str(working_directory / "missing_file.txt")])

    assert "Error processing file" in capsys.readouterr().out
    assert not (working_directory / "pynesthesia_output").exists()


def test_cli_colorizes(capsys):
    """check that colorize prints colored text"""
    cli.main(["colorize", "0f"])

    assert capsys.readouterr().out.strip() == colors.colorize("0f")


def test_chiptune_from_file(working_directory, capsys):
    """check that a file creates a chiptune wav"""
    file = working_directory / "chiptune_test.txt"
    file.write_bytes(b"hello")
    cli.main(["chiptune", str(file)])
    outputs = list((working_directory / "pynesthesia_output" / "chiptunes").glob("*.wav"))

    assert len(outputs) == 1
    assert outputs[0].read_bytes()[:4] == b"RIFF"
    assert "_bars-4_wave-square.wav" in outputs[0].name
    assert str(outputs[0]) in capsys.readouterr().out


def test_chiptune_options_change_the_name(working_directory):
    """check that --bars and --wave end up in the filename"""
    file = working_directory / "chiptune_test.txt"
    file.write_bytes(b"hello")
    cli.main(["chiptune", str(file), "--bars", "1", "--wave", "saw"])
    outputs = list((working_directory / "pynesthesia_output" / "chiptunes").glob("*.wav"))

    assert len(outputs) == 1
    assert outputs[0].name.endswith("_bars-1_wave-saw.wav")
    assert outputs[0].stat().st_size > 0


def test_chiptune_is_repeatable(working_directory):
    """check that the same file makes the same wav"""
    file = working_directory / "same_chiptune.txt"
    file.write_bytes(b"hello")
    cli.main(["chiptune", str(file), "--bars", "1"])
    directory = working_directory / "pynesthesia_output" / "chiptunes"
    output = next(directory.glob("*.wav"))
    first_audio = output.read_bytes()

    cli.main(["chiptune", str(file), "--bars", "1"])

    assert list(directory.glob("*.wav")) == [output]
    assert output.read_bytes() == first_audio


def test_chiptune_with_missing_file(working_directory, capsys):
    """check that a missing file creates no chiptune"""
    cli.main(["chiptune", str(working_directory / "missing_chiptune.txt")])

    assert "Error processing file" in capsys.readouterr().out
    assert not (working_directory / "pynesthesia_output").exists()


def test_invalid_chiptune_commands(tmp_path):
    """check that invalid chiptune commands are rejected"""
    file = str(tmp_path / "input.txt")
    commands = [
        ["chiptune"],
        ["chiptune", "relative.txt"],
        ["chiptune", file, "--bars", "0"],
        ["chiptune", file, "--bars", "33"],
        ["chiptune", file, "--wave", "kazoo"],
        ["--colorize", "0f", "chiptune", file],
    ]
    for command in commands:
        # argparse uses exit code 2 for errors
        with pytest.raises(SystemExit) as error:
            cli.main(command)

        assert error.value.code == 2


def test_cannot_save_chiptune(working_directory, capsys, monkeypatch):
    """check that a chiptune save error is reported"""
    file = working_directory / "input.txt"
    file.write_bytes(b"hello")

    # Simulate save error without changing the working directory
    def fail_write(*args, **kwargs):
        raise OSError("permission denied")

    monkeypatch.setattr(Path, "write_bytes", fail_write)

    with pytest.raises(SystemExit) as error:
        cli.main(["chiptune", str(file)])

    assert error.value.code == 2
    assert "could not save output" in capsys.readouterr().err

def test_flower_from_file(working_directory, capsys):
    """Check that a file creates an svg flower"""
    file = working_directory / "flower_test.txt"
    file.write_bytes(b"hello")
    cli.main(["flower", str(file)])
    outputs = list(
        (working_directory / "pynesthesia_output" / "flower").glob("*.svg")
    )

    assert len(outputs) == 1
    assert outputs[0].stat().st_size > 0
    assert outputs[0].read_text(encoding="utf-8").startswith("<svg") 
    assert str(outputs[0]) in capsys.readouterr().out

def test_flower_is_repeatable(working_directory):
    """Check that the same input file gives the same svg flower"""
    file = working_directory / "same_flower.txt"
    file.write_bytes(b"hello")
    cli.main(["flower", str(file)])
    directory = working_directory / "pynesthesia_output" / "flower"
    output = next(directory.glob("*.svg"))
    first_svg = output.read_bytes()

    cli.main(["flower", str(file)])

    assert list(directory.glob("*.svg")) == [output]
    assert output.read_bytes() == first_svg

def test_flower_with_missing_file(working_directory, capsys):
    """Check that a missing file creates no svg flower"""
    cli.main(["flower", str(working_directory / "missing_flower.txt")])

    assert "Error processing file" in capsys.readouterr().out
    assert not (working_directory / "pynesthesia_output").exists()