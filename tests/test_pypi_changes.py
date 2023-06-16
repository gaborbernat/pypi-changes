from __future__ import annotations

from typing import TYPE_CHECKING

from virtualenv import cli_run

from pypi_changes import main

if TYPE_CHECKING:
    from pathlib import Path


def test_pypi_changes_self_output_default(tmp_path: Path) -> None:
    venv = cli_run([str(tmp_path / "venv")], setup_logging=False)
    main([str(venv.creator.exe), "--cache-path", str(tmp_path / "a.sqlite")])


def test_pypi_changes_self_output_json(tmp_path: Path) -> None:
    venv = cli_run([str(tmp_path / "venv")], setup_logging=False)
    main([str(venv.creator.exe), "--output", "json"])
