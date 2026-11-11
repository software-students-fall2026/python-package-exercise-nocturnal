import os
import runpy
import sys
from pathlib import Path


def test_main_runs_cli(tmp_path, capsys):
    """check that the package starts the command line"""
    file = tmp_path / "input.txt"
    file.write_bytes(b"hello")
    output_directory = tmp_path / "jingles"

    # pass a file path to the package
    previous_args = sys.argv
    previous_directory = Path.cwd()
    try:
        os.chdir(tmp_path)
        sys.argv = ["pynesthesia", "jingle", str(file)]

        # run the package from the command line
        runpy.run_module("pynesthesia", run_name="__main__")
    finally:
        # restore the original arguments and directory
        sys.argv = previous_args
        os.chdir(previous_directory)

    outputs = list(output_directory.glob("*.mp3"))

    assert len(outputs) == 1
    assert str(outputs[0]) in capsys.readouterr().out