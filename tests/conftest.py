from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, create_autospec

import pytest

from pypi_changes._cli import Options
from tests import MakeDist


@pytest.fixture()
def option_simple(tmp_path: Path) -> Options:
    return Options(cache_path=tmp_path / "a.sqlite", jobs=1, cache_duration=0.01)


@pytest.fixture()
def make_dist() -> MakeDist:
    def func(path: Path, name: str, version: str) -> MagicMock:
        of_type = f"importlib{'.' if sys.version_info >= (3, 8) else '_'}metadata.PathDistribution"
        dist: MagicMock = create_autospec(of_type)
        dist.metadata = {"Name": name}
        dist._path = path / "dist"
        dist.version = version
        return dist

    return func
