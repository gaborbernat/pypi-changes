from __future__ import annotations

from pathlib import Path

from virtualenv import cli_run

from pypi_changes import main


def test_pypi_changes_self(tmp_path: Path) -> None:
    venv = cli_run([str(tmp_path / "venv")], setup_logging=False)
    main([str(venv.creator.exe), "--cache-path", str(tmp_path / "a.sqlite")])
