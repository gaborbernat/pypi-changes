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


def test_cli_ok_default(tmp_path: Path, mocker: MockerFixture) -> None:
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


def test_cli_python_not_exist(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as context:
        parse_cli_arguments([str(tmp_path / "missing")])

    assert context.value.code == 2
    out, err = capsys.readouterr()
    assert not out
    assert f"pypi-changes: error: argument PYTHON_EXE: path {tmp_path / 'missing'} does not exist" in err
