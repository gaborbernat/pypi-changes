from __future__ import annotations

from collections.abc import Callable
from importlib.metadata import PathDistribution
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from pypi_changes._cli import Options

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock import MockerFixture

MakeDist = Callable[[Path, str, str], PathDistribution]


@pytest.fixture(autouse=True)
def _no_index(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("PIP_INDEX_URL", raising=False)


@pytest.fixture(autouse=True)
def _no_proxy(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("https_proxy", raising=False)
    monkeypatch.delenv("http_proxy", raising=False)
    monkeypatch.delenv("no_proxy", raising=False)


@pytest.fixture
def option_simple(tmp_path: Path) -> Options:
    return Options(cache_path=tmp_path / "a.sqlite", jobs=1, cache_duration=0.01)


@pytest.fixture
def make_dist(mocker: MockerFixture) -> MakeDist:
    def func(path: Path, name: str, version: str) -> PathDistribution:
        return mocker.create_autospec(
            PathDistribution, instance=True, metadata={"Name": name}, _path=path / "dist", version=version
        )

    return func
