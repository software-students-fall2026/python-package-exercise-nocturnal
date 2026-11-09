import runpy
from unittest.mock import patch


def test_main_runs_cli():
    """check that the package starts the cli"""
    # replace the cli function so the test does not need a file path
    with patch("pynesthesia.cli.hash_file") as hash_file:
        # run the package as if it were started from the command line
        runpy.run_module("pynesthesia", run_name="__main__")

    hash_file.assert_called_once_with()