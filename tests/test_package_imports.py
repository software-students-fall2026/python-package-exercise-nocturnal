import subprocess
import sys


def test_package_imports(tmp_path):
    """check that the installed package imports outside the project"""
    result = subprocess.run(
        [sys.executable, "-c", "import pynesthesia"],
        cwd=tmp_path, capture_output=True, text=True,
    )

    assert result.returncode == 0
