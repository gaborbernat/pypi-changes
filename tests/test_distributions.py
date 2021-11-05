from __future__ import annotations

import sys
from pathlib import Path

from pypi_changes._cli import Options
from pypi_changes._distributions import collect_distributions

if sys.version_info >= (3, 8):  # pragma: no cover (py38+)
    from importlib.metadata import PathDistribution
else:  # pragma: no cover (<py38)
    from importlib_metadata import PathDistribution


def test_distributions() -> None:
    distributions = list(collect_distributions(Options(python=Path(sys.executable))))
    assert all(isinstance(i, PathDistribution) for i in distributions)
