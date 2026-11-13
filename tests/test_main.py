from __future__ import annotations

import subprocess  # ruff:ignore[suspicious-subprocess-import]  # the tests run the installed entry points
import sys
from pathlib import Path

import pytest


def test_help_module() -> None:
    subprocess.check_call([sys.executable, "-m", "pypi_changes", "--help"])


@pytest.mark.parametrize("name", [pytest.param("python.exe" if sys.platform == "win32" else "python", id="console")])
def test_help_console(name: str) -> None:
    subprocess.check_call(  # ruff:ignore[subprocess-without-shell-equals-true]  # fixed argv tests console entry point
        [str(Path(sys.executable).parent / name), "--help"]
    )
