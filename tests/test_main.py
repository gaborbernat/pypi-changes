from __future__ import annotations

import subprocess  # ruff:ignore[suspicious-subprocess-import]
import sys
from pathlib import Path

import pytest


def test_help_module() -> None:
    subprocess.check_call([sys.executable, "-m", "pypi_changes", "--help"])


@pytest.mark.parametrize("name", ["python.exe" if sys.platform == "win32" else "python"])
def test_help_console(name: str) -> None:
    subprocess.check_call([str(Path(sys.executable).parent / name), "--help"])
