from __future__ import annotations

import os
from datetime import UTC, datetime
from itertools import count
from operator import attrgetter
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pypi_simple import DistributionPackage, ProjectPage, PyPISimple
from requests import Response
from rich.console import Console
from rich.progress import Progress, ProgressColumn
from vcr import use_cassette
from vcr.stubs import VCRHTTPResponse

from pypi_changes._info import _merge_with_index_server, pypi_info  # ruff:ignore[import-private-name]  # test index merge

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from tests.conftest import MakeDist, Options


@pytest.fixture(autouse=True)  # ruff:ignore[pytest-fixture-autouse]  # vcrpy replay needs this shim in every test
def _vcr_response_request_url(monkeypatch: pytest.MonkeyPatch) -> None:
    # requests-cache reads urllib3 2's HTTPResponse._request_url (backing its url), which vcrpy's replay stub lacks
    monkeypatch.setattr(VCRHTTPResponse, "_request_url", property(attrgetter("url")), raising=False)


@pytest.fixture
def _force_pypi_index(mocker: MockerFixture, _no_index: None) -> None:
    mocker.patch("pypi_changes._info.PYPI_INDEX", "")
    mocker.patch.dict(os.environ, {"PIP_INDEX_URL": "https://pypi.org/simple"})


@pytest.mark.usefixtures("_force_pypi_index")
def test_info_self(tmp_path: Path, option_simple: Options, make_dist: MakeDist) -> None:
    distributions = [make_dist(tmp_path, "pypi-changes", "1.0.0")]

    with use_cassette(str(Path(__file__).parents[1] / "pypi_info_self.yaml"), mode="once"):
        packages = list(pypi_info(distributions, option_simple))

    assert isinstance(packages, list)
    assert len(packages) == 1
    pkg = packages[0]
    assert repr(pkg) == f"Package(name='pypi-changes', path={(tmp_path / 'dist')!r})"


def test_synthesized_release(
    tmp_path: Path, option_simple: Options, make_dist: MakeDist, mocker: MockerFixture
) -> None:
    response = mocker.create_autospec(Response, instance=True, ok=True)
    response.configure_mock(**{
        "json.return_value": {
            "releases": {
                "2": [{"upload_time_iso_8601": "2021-01-02T00:00:00+00:00"}],
                "1": [],
            },
        }
    })
    mocker.patch("pypi_changes._info.CachedSession.get", autospec=True, return_value=response)

    packages = list(pypi_info([make_dist(tmp_path, "a", "1")], option_simple))

    assert packages[0].info == {
        "releases": {
            "2": [{"version": "2", "upload_time_iso_8601": datetime(2021, 1, 2, tzinfo=UTC)}],
            "1": [
                {
                    "packagetype": "sdist",
                    "version": "1",
                    "upload_time_iso_8601": datetime(2021, 1, 1, 23, 59, 59, tzinfo=UTC),
                    "synthesized": True,
                },
            ],
        },
    }


def test_progress_speed(tmp_path: Path, option_simple: Options, make_dist: MakeDist, mocker: MockerFixture) -> None:
    response = mocker.create_autospec(Response, instance=True, ok=True)
    response.configure_mock(**{"json.return_value": {"releases": {}}})
    mocker.patch("pypi_changes._info.CachedSession.get", autospec=True, return_value=response)
    clock = count()
    progresses: list[Progress] = []

    def make_progress(*columns: str | ProgressColumn, transient: bool) -> Progress:
        progress = Progress(*columns, transient=transient, get_time=lambda: next(clock), auto_refresh=False)
        progresses.append(progress)
        return progress

    mocker.patch("pypi_changes._info.Progress", autospec=True, side_effect=make_progress)

    list(pypi_info([make_dist(tmp_path, "a", "1"), make_dist(tmp_path, "b", "1")], option_simple))

    console = Console(record=True, width=200)
    console.print(progresses[0].get_renderable())
    output = console.export_text()
    assert "steps/s" in output
    assert "no speed" not in output


@pytest.mark.usefixtures("_force_pypi_index")
@pytest.mark.usefixtures("_no_proxy")
def test_info_missing(tmp_path: Path, option_simple: Options, make_dist: MakeDist) -> None:
    distributions = [make_dist(tmp_path, "missing-package", "1.0.0")]

    with use_cassette(str(Path(__file__).parents[1] / "pypi_info_missing_package.yaml"), mode="once"):
        packages = list(pypi_info(distributions, option_simple))

    assert isinstance(packages, list)
    assert len(packages) == 1
    pkg = packages[0]
    assert pkg.info is None
    assert pkg.last_release_at is None


@pytest.mark.usefixtures("_no_proxy")
def test_info_pypi_server_invalid_version(tmp_path: Path, option_simple: Options, make_dist: MakeDist) -> None:
    dist = make_dist(tmp_path, "pytz", "1.0")

    with use_cassette(str(Path(__file__).parents[1] / "pypi_info_pytz.yaml"), mode="once"):
        packages = list(pypi_info([dist], option_simple))

    assert isinstance(packages, list)
    assert len(packages) == 1
    pkg = packages[0]
    assert pkg.exc is None
    assert pkg.info is not None
    assert "2004b" in pkg.info["releases"]  # this is an invalid version


def test_info_pypi_server_timeout(
    tmp_path: Path,
    mocker: MockerFixture,
    option_simple: Options,
    make_dist: MakeDist,
) -> None:
    dist = make_dist(tmp_path, "a", "1.0")
    mocker.patch(
        "pypi_changes._info.CachedSession", autospec=True
    ).return_value.__enter__.return_value.get.side_effect = TimeoutError

    packages = list(pypi_info([dist], option_simple))

    assert isinstance(packages, list)
    assert len(packages) == 1
    pkg = packages[0]
    assert pkg.info is None
    assert isinstance(pkg.exc, TimeoutError)


def test_merge_with_pypi(mocker: MockerFixture) -> None:
    versions = [("2", "sdist"), ("1", "sdist"), (None, None), ("3", "wheel")]
    packages = [mocker.create_autospec(DistributionPackage, version=v, package_type=t) for v, t in versions]
    page = mocker.create_autospec(ProjectPage, packages=packages)
    client = mocker.create_autospec(PyPISimple, spec_set=True)
    client.get_project_page.return_value = page

    result = _merge_with_index_server(
        "a", client, {"0": [{"packagetype": "sdist", "upload_time_iso_8601": None, "version": "0"}]}
    )
    assert result == {
        "0": [{"packagetype": "sdist", "upload_time_iso_8601": None, "version": "0"}],
        "1": [{"packagetype": "sdist", "upload_time_iso_8601": None, "version": "1"}],
        "2": [{"packagetype": "sdist", "upload_time_iso_8601": None, "version": "2"}],
        "3": [{"packagetype": "wheel", "upload_time_iso_8601": None, "version": "3"}],
    }
