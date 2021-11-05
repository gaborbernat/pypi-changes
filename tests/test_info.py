from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import create_autospec

from pytest_mock import MockerFixture
from vcr import use_cassette

from pypi_changes._cli import Options
from pypi_changes._info import pypi_info
from pypi_changes._pkg import Package


def test_pypi_info_self(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch("pypi_changes._info.PYPI_INDEX", "")
    mocker.patch.dict(os.environ, {"PIP_INDEX_URL": "https://pypi.org/simple"})

    dist = create_autospec(f"importlib{'.' if sys.version_info >= (3, 8) else '_'}metadata.PathDistribution")
    dist.metadata = {"Name": "pypi-changes"}
    dist._path = tmp_path / "dist"

    options = Options(cache_path=tmp_path / "a.sqlite", jobs=1, cache_duration=0.01)
    distributions = [dist]

    with use_cassette(str(Path(__file__).parent / "pypi_info_self.yaml"), mode="once"):
        packages = list(pypi_info(distributions, options))

    assert isinstance(packages, list)
    assert len(packages) == 1
    pkg = packages[0]
    assert isinstance(pkg, Package)
    assert repr(pkg) == f"Package(name='pypi-changes', path={repr(tmp_path / 'dist')})"
