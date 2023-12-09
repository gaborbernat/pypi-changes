from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from pypi_changes._cli import Options
from pypi_changes._distributions import collect_distributions
from tests import PathDistribution

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_distributions() -> None:
    distributions = list(collect_distributions(Options(python=Path(sys.executable))))
    assert all(isinstance(i, PathDistribution) for i in distributions)


def _make_dist(path: Path, name: str) -> Path:
    dist = path / f"{name}.dist-info"
    dist.mkdir(parents=True)
    (dist / "METADATA").write_text(f"Name: {name}")
    return dist


def test_distribution_duplicate_path(mocker: MockerFixture, tmp_path: Path) -> None:
    dist = _make_dist(tmp_path, "a")
    mocker.patch("pypi_changes._distributions._get_py_info", return_value=[dist.parent] * 2)
    distributions = list(collect_distributions(Options(python=Path(sys.executable))))
    assert len(distributions) == 1
    assert distributions[0].metadata["Name"] == "a"


def test_distribution_duplicate_pkg(mocker: MockerFixture, tmp_path: Path) -> None:
    dist_1, dist_2 = _make_dist(tmp_path / "1", "a"), _make_dist(tmp_path / "2", "a")
    mocker.patch("pypi_changes._distributions._get_py_info", return_value=[dist_1.parent, dist_2.parent])
    distributions = list(collect_distributions(Options(python=Path(sys.executable))))
    assert len(distributions) == 1
    assert distributions[0].metadata["Name"] == "a"
    assert distributions[0]._path == dist_1  # noqa: SLF001
