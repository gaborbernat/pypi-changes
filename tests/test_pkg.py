from __future__ import annotations

from pathlib import Path

from pypi_changes._pkg import Package
from tests import MakeDist


def test_ignore_dev_release(make_dist: MakeDist, tmp_path: Path) -> None:
    releases = {"releases": {"1.0.0dev1": [{"version": "1.0.0dev1"}], "0.9.0": [{"version": "0.9.0"}]}}
    pkg = Package(make_dist(tmp_path, "a", "1.0.0"), info=releases)
    assert pkg.last_release == {"version": "0.9.0"}


def test_fallback_to_rc_release(make_dist: MakeDist, tmp_path: Path) -> None:
    pkg = Package(make_dist(tmp_path, "a", "1.0.0"), info={"releases": {"1.0.0rc1": [{"version": "1.0.0rc1"}]}})
    assert pkg.last_release == {"version": "1.0.0rc1"}
