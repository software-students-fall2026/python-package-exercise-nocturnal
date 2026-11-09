import hashlib
import runpy
import sys


def test_main_runs_cli(tmp_path, capsys):
    file = tmp_path / "input.txt"
    file.write_bytes(b"hello")
    expected = hashlib.sha256(b"hello").hexdigest()

    # give the package a file path as a command line argument
    previous = sys.argv
    try:
        sys.argv = ["pynesthesia", str(file)]

        # run the package as if it were started from the command line
        runpy.run_module("pynesthesia", run_name="__main__")
    finally:
        # restore the original arguments after the test
        sys.argv = previous

    assert capsys.readouterr().out.strip() == expected
