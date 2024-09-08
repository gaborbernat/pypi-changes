from __future__ import annotations

import subprocess  # noqa: S404
import sys
from pathlib import Path


def test_help_module() -> None:
    subprocess.check_call([sys.executable, "-m", "pypi_changes", "--help"])


def test_help_console() -> None:
    cli = Path(sys.executable).parent / f"python{'.exe' if sys.platform == 'win32' else ''}"
    subprocess.check_call([str(cli), "--help"])
