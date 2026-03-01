from __future__ import annotations

from datetime import datetime, timezone
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


def test_last_release_at_synthesized(make_dist: MakeDist, tmp_path: Path) -> None:
    release = {
        "version": "1.0.0",
        "upload_time_iso_8601": datetime(2021, 1, 1, tzinfo=timezone.utc),
        "synthesized": True,
    }
    pkg = Package(make_dist(tmp_path, "a", "0.9.0"), info={"releases": {"1.0.0": [release]}})

    assert pkg.last_release_at is None


def test_last_release_at_real(make_dist: MakeDist, tmp_path: Path) -> None:
    upload_time = datetime(2021, 1, 1, tzinfo=timezone.utc)
    release = {"version": "1.0.0", "upload_time_iso_8601": upload_time}
    pkg = Package(make_dist(tmp_path, "a", "0.9.0"), info={"releases": {"1.0.0": [release]}})

    assert pkg.last_release_at == upload_time


def test_last_release_at_no_info(make_dist: MakeDist, tmp_path: Path) -> None:
    pkg = Package(make_dist(tmp_path, "a", "1.0.0"), info=None)

    assert pkg.last_release_at is None
