from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import call

import pytest

from pypi_changes import __version__
from pypi_changes._cli import Options, parse_cli_arguments

if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.capture import CaptureFixture
    from pytest_mock import MockerFixture


def test_cli_ok_explicit_python(tmp_path: Path, mocker: MockerFixture) -> None:
    user_cache_path = mocker.patch("pypi_changes._cli.user_cache_path", return_value=tmp_path / "cache")

    options = parse_cli_arguments([str(tmp_path)])

    assert isinstance(options, Options)
    assert options.__dict__ == {
        "jobs": 10,
        "cache_path": tmp_path / "cache" / "requests.sqlite",
        "cache_duration": 3600,
        "python": tmp_path,
        "sort": "updated",
        "output": "tree",
    }
    assert user_cache_path.call_args == call(appname="pypi_changes", appauthor="gaborbernat", version=__version__)


def test_cli_default_python_from_path(tmp_path: Path, mocker: MockerFixture) -> None:
    python_path = tmp_path / "python"
    python_path.touch()
    mocker.patch("pypi_changes._cli.shutil.which", return_value=str(python_path))
    mocker.patch("pypi_changes._cli.user_cache_path", return_value=tmp_path / "cache")

    options = parse_cli_arguments([])

    assert options.python == python_path.absolute()


def test_cli_default_python_not_found(mocker: MockerFixture, capsys: CaptureFixture[str]) -> None:
    mocker.patch("pypi_changes._cli.shutil.which", return_value=None)

    with pytest.raises(SystemExit) as context:
        parse_cli_arguments([])

    assert context.value.code == 2
    out, err = capsys.readouterr()
    assert not out
    assert "no python interpreter found on PATH" in err


def test_cli_python_not_exist(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as context:
        parse_cli_arguments([str(tmp_path / "missing")])

    assert context.value.code == 2
    out, err = capsys.readouterr()
    assert not out
    assert f"pypi-changes: error: argument PYTHON_EXE: path {tmp_path / 'missing'} does not exist" in err
