from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from vcr import use_cassette

from pypi_changes._cli import Options
from pypi_changes._info import pypi_info
from pypi_changes._pkg import Package
from tests import MakeDist


@pytest.fixture()
def _force_pypi_index(mocker: MockerFixture) -> None:
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
    assert repr(pkg) == f"Package(name='pypi-changes', path={repr(tmp_path / 'dist')})"


@pytest.mark.usefixtures("_force_pypi_index")
def test_info_missing(tmp_path: Path, option_simple: Options, make_dist: MakeDist) -> None:
    dist = make_dist(tmp_path, "missing-package", "1.0.0")
    distributions = [dist]

    with use_cassette(str(Path(__file__).parent / "pypi_info_missing_package.yaml"), mode="once"):
        packages = list(pypi_info(distributions, option_simple))

    assert isinstance(packages, list)
    assert len(packages) == 1
    pkg = packages[0]
    assert pkg.info == {"releases": {}}
    current = datetime.now(timezone.utc)
    last_release_at = pkg.last_release_at
    assert current <= last_release_at


def test_info_pypi_server_invalid_version(tmp_path: Path, option_simple: Options, make_dist: MakeDist) -> None:
    dist = make_dist(tmp_path, "pytz", "1.0")

    with use_cassette(str(Path(__file__).parent / "pypi_info_pytz.yaml"), mode="once"):
        packages = list(pypi_info([dist], option_simple))

    assert isinstance(packages, list)
    assert len(packages) == 1
    pkg = packages[0]
    assert pkg.info is not None
    assert "2004b" in pkg.info["releases"]  # this is an invalid version


def test_info_pypi_server_timeout(
    tmp_path: Path, mocker: MockerFixture, option_simple: Options, make_dist: MakeDist
) -> None:
    dist = make_dist(tmp_path, "a", "1.0")
    mocker.patch("requests.Session.get", side_effect=TimeoutError)
    packages = list(pypi_info([dist], option_simple))

    assert isinstance(packages, list)
    assert len(packages) == 1
    pkg = packages[0]
    assert pkg.info is None
    assert isinstance(pkg.exc, TimeoutError)
