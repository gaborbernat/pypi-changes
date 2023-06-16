from __future__ import annotations

from typing import TYPE_CHECKING

from pypi_changes._pkg import Package

if TYPE_CHECKING:
    from pathlib import Path

    from tests import MakeDist


def test_ignore_dev_release(make_dist: MakeDist, tmp_path: Path) -> None:
    releases = {"releases": {"1.0.0dev1": [{"version": "1.0.0dev1"}], "0.9.0": [{"version": "0.9.0"}]}}
    pkg = Package(make_dist(tmp_path, "a", "1.0.0"), info=releases)
    assert pkg.last_release == {"version": "0.9.0"}


def test_fallback_to_rc_release(make_dist: MakeDist, tmp_path: Path) -> None:
    pkg = Package(make_dist(tmp_path, "a", "1.0.0"), info={"releases": {"1.0.0rc1": [{"version": "1.0.0rc1"}]}})
    assert pkg.last_release == {"version": "1.0.0rc1"}


def test_current_release_parse_ok(make_dist: MakeDist, tmp_path: Path) -> None:
    pkg = Package(make_dist(tmp_path, "a", "1.0.0"), info={"releases": {"1.0.0": [{"version": "1.0.0"}]}})
    assert pkg.current_release == {"version": "1.0.0"}


def test_current_release_empty(make_dist: MakeDist, tmp_path: Path) -> None:
    pkg = Package(make_dist(tmp_path, "a", "1.0.0"), info=None)
    assert pkg.current_release == {}
