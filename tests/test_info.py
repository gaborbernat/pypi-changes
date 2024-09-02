from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import create_autospec

import pytest
from pypi_simple import DistributionPackage, ProjectPage, PyPISimple
from vcr import use_cassette

from pypi_changes._info import _merge_with_index_server, pypi_info
from pypi_changes._pkg import Package

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from pypi_changes._cli import Options
    from tests import MakeDist


@pytest.fixture
def _force_pypi_index(mocker: MockerFixture, _no_index: None) -> None:
    mocker.patch("pypi_changes._info.PYPI_INDEX", "")
    mocker.patch.dict(os.environ, {"PIP_INDEX_URL": "https://pypi.org/simple"})


@pytest.mark.usefixtures("_force_pypi_index")
def test_info_self(tmp_path: Path, option_simple: Options, make_dist: MakeDist) -> None:
    dist = make_dist(tmp_path, "pypi-changes", "1.0.0")
    distributions = [dist]

    with use_cassette(str(Path(__file__).parent / "pypi_info_self.yaml"), mode="once"):
        packages = list(pypi_info(distributions, option_simple))

    assert isinstance(packages, list)
    assert len(packages) == 1
    pkg = packages[0]
    assert isinstance(pkg, Package)
    assert repr(pkg) == f"Package(name='pypi-changes', path={tmp_path / 'dist'!r})"


@pytest.mark.usefixtures("_force_pypi_index")
@pytest.mark.usefixtures("_no_proxy")
def test_info_missing(tmp_path: Path, option_simple: Options, make_dist: MakeDist) -> None:
    dist = make_dist(tmp_path, "missing-package", "1.0.0")
    distributions = [dist]

    with use_cassette(str(Path(__file__).parent / "pypi_info_missing_package.yaml"), mode="once"):
        packages = list(pypi_info(distributions, option_simple))

    assert isinstance(packages, list)
    assert len(packages) == 1
    pkg = packages[0]
    assert pkg.info is None
    current = datetime.now(timezone.utc)
    last_release_at = pkg.last_release_at
    assert current <= last_release_at


@pytest.mark.usefixtures("_no_proxy")
def test_info_pypi_server_invalid_version(tmp_path: Path, option_simple: Options, make_dist: MakeDist) -> None:
    dist = make_dist(tmp_path, "pytz", "1.0")

    with use_cassette(str(Path(__file__).parent / "pypi_info_pytz.yaml"), mode="once"):
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
    mock_cached_session = mocker.patch("pypi_changes._info.CachedSession")
    mock_cached_session.return_value.__enter__.return_value.get.side_effect = TimeoutError

    packages = list(pypi_info([dist], option_simple))

    assert isinstance(packages, list)
    assert len(packages) == 1
    pkg = packages[0]
    assert pkg.info is None
    assert isinstance(pkg.exc, TimeoutError)


def test_merge_with_pypi() -> None:
    versions = [("2", "sdist"), ("1", "sdist"), (None, None), ("3", "wheel")]
    packages = [create_autospec(DistributionPackage, version=v, package_type=t) for v, t in versions]
    page = create_autospec(ProjectPage, packages=packages)
    client = create_autospec(PyPISimple, spec_set=True)
    client.get_project_page.return_value = page

    start = {"0": [{"packagetype": "sdist", "upload_time_iso_8601": None, "version": "0"}]}
    result = _merge_with_index_server("a", client, start)
    assert result == {
        "0": [{"packagetype": "sdist", "upload_time_iso_8601": None, "version": "0"}],
        "1": [{"packagetype": "sdist", "upload_time_iso_8601": None, "version": "1"}],
        "2": [{"packagetype": "sdist", "upload_time_iso_8601": None, "version": "2"}],
        "3": [{"packagetype": "wheel", "upload_time_iso_8601": None, "version": "3"}],
    }
