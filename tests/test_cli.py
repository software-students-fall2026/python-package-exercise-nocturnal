import hashlib
import runpy
import sys

import pytest

from pynesthesia.cli import main


def test_cli_prints_file_hash(tmp_path, capsys):
    """simulate hashing a text file"""
    file = tmp_path / "random.txt"
    random_bytes = b"random text file"

    file.write_bytes(random_bytes)
    expected_output = hashlib.sha256(random_bytes).hexdigest()

    assert main([str(file)]) == 0
    assert capsys.readouterr().out.strip() == expected_output


def test_cli_returns_failure_for_missing_file(tmp_path, capsys):
    """simulate file not found error condition"""
    filepath = tmp_path / "missing.txt"

    assert main([str(filepath)]) == 1
    assert "Error processing file" in capsys.readouterr().out


def test_cli_requires_a_path(capsys):
    """simulate missing file path"""
    with pytest.raises(SystemExit) as exc:
        main([])

    assert exc.value.code == 2
    assert "path" in capsys.readouterr().err


def test_module_entry_point(tmp_path, monkeypatch, capsys):
    """simulate running the package"""
    file = tmp_path / "random.txt"
    random_bytes = b"random text file"

    file.write_bytes(random_bytes)
    expected_output = hashlib.sha256(random_bytes).hexdigest()
    # set command line arguments for this test
    # monkeypatch restores the original arguments afterward
    monkeypatch.setattr(sys, "argv", ["pynesthesia", str(file)])

    with pytest.raises(SystemExit) as exc:
        runpy.run_module("pynesthesia", run_name="__main__")

    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == expected_output
