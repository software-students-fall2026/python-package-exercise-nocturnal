import os
import runpy
import sys
from pathlib import Path


def test_main_runs_cli(tmp_path, capsys):
    file = tmp_path / "input.txt"
    file.write_bytes(b"hello")
    output = tmp_path / "jingle.mid"

    # give the package a file path as a command line argument
    previous_args = sys.argv
    previous_directory = Path.cwd()
    try:
        os.chdir(tmp_path)
        sys.argv = ["pynesthesia", "jingle", str(file)]

        # run the package as if it were started from the command line
        runpy.run_module("pynesthesia", run_name="__main__")
    finally:
        # restore the original arguments and directory after the test
        sys.argv = previous_args
        os.chdir(previous_directory)

    assert output.exists()
    assert str(output) in capsys.readouterr().out
