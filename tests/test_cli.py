import hashlib
import subprocess
import sys

import pytest

import pynesthesia.cli as cli


def test_cli_prints_file_hash(tmp_path, capsys):
    """simulate hashing a text file"""
    file = tmp_path / "random.txt"
    random_bytes = b"random text file"

    file.write_bytes(random_bytes)
    expected_output = hashlib.sha256(random_bytes).hexdigest()

    cli.hash_file([str(file)])
    assert capsys.readouterr().out.strip() == expected_output


def test_cli_with_missing_file(tmp_path, capsys):
    """simulate file not found error condition"""
    filepath = tmp_path / "missing.txt"

    cli.hash_file([str(filepath)])
    assert "Error processing file" in capsys.readouterr().out


def test_cli_requires_a_path(capsys):
    """simulate missing file path"""
    # argparse exits when the required path is missing
    with pytest.raises(SystemExit) as exc:
        cli.hash_file([])

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
