from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest
from requests import Response

from pypi_changes import __version__
from pypi_changes._cli import Options, main, parse_cli_arguments  # ruff:ignore[import-private-name]  # test CLI internals

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

    from tests.conftest import MakeDist


def test_requirements_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], mocker: MockerFixture, make_dist: MakeDist
) -> None:
    mocker.patch(
        "pypi_changes._cli.collect_distributions",
        autospec=True,
        return_value=[make_dist(tmp_path, "a", "1")],
    )
    response = mocker.create_autospec(Response, instance=True, ok=True)
    response.configure_mock(**{
        "json.return_value": {
            "releases": {
                "2": [{"upload_time_iso_8601": "2021-01-01T00:00:00+00:00", "packagetype": "sdist"}],
            },
        }
    })
    mocker.patch("pypi_changes._info.CachedSession.get", autospec=True, return_value=response)

    result = main([sys.executable, "--output", "requirements", "--cache-path", str(tmp_path / "cache")])

    out, err = capsys.readouterr()
    assert (result, out.strip(), err) == (0, "a==2", "")


def test_cli_ok_explicit_python(tmp_path: Path, mocker: MockerFixture) -> None:
    user_cache_path = mocker.patch("pypi_changes._cli.user_cache_path", autospec=True, return_value=tmp_path / "cache")

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
    assert user_cache_path.call_args == mocker.call(
        appname="pypi_changes", appauthor="gaborbernat", version=__version__
    )


def test_cli_default_python_from_path(tmp_path: Path, mocker: MockerFixture) -> None:
    python_path = tmp_path / "python"
    python_path.touch()
    mocker.patch("pypi_changes._cli.shutil.which", autospec=True, return_value=str(python_path))
    mocker.patch("pypi_changes._cli.user_cache_path", autospec=True, return_value=tmp_path / "cache")

    options = parse_cli_arguments([])

    assert options.python == python_path.absolute()


def test_cli_default_python_not_found(mocker: MockerFixture, capsys: pytest.CaptureFixture[str]) -> None:
    mocker.patch("pypi_changes._cli.shutil.which", autospec=True, return_value=None)

    with pytest.raises(SystemExit) as context:
        parse_cli_arguments([])

    assert context.value.code == 2  # ruff:ignore[magic-value-comparison]  # argparse exits with status 2
    out, err = capsys.readouterr()
    assert not out
    assert "no python interpreter found on PATH" in err


def test_cli_python_not_exist(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as context:
        parse_cli_arguments([str(tmp_path / "missing")])

    assert context.value.code == 2  # ruff:ignore[magic-value-comparison]  # argparse exits with status 2
    out, err = capsys.readouterr()
    assert not out
    assert f"pypi-changes: error: argument PYTHON_EXE: path {tmp_path / 'missing'} does not exist" in err
