from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import create_autospec

from vcr import use_cassette

from pypi_changes._cli import Options
from pypi_changes._info import pypi_info


def test_pypi_info_self(tmp_path: Path) -> None:
    dist = create_autospec(f"importlib{'.' if sys.version_info >= (3, 8) else '_'}metadata.PathDistribution")
    dist.metadata = {"Name": "pypi-changes"}
    options = Options(cache_path=tmp_path / "a.sqlite", jobs=1, cache_duration=0.01)
    distributions = [dist]

    with use_cassette(str(Path(__file__).parent / "pypi_info_self.yaml"), mode="once"):
        result = list(pypi_info(distributions, options))

    assert result
