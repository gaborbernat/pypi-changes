from __future__ import annotations  # noqa: A005

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from humanize import naturaldelta

from . import get_sorted_pkg_list

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pypi_changes._cli import Options
    from pypi_changes._pkg import Package


def release_info(release: dict[str, Any] | None, now: datetime) -> dict[str, Any]:
    if release is None:
        return {}
    release_at = release.get("upload_time_iso_8601")
    release_since = naturaldelta(now - release_at) if release_at else None
    return {
        "version": release.get("version"),
        "date": release_at.isoformat() if release_at is not None else None,
        "since": release_since,
    }


def print_json(distributions: Iterable[Package], options: Options) -> None:
    now = datetime.now(timezone.utc)
    pkg_list = []

    for pkg in get_sorted_pkg_list(distributions, options, now):
        current_release = {"version": pkg.version, **release_info(pkg.current_release, now)}
        latest_release = release_info(pkg.last_release, now)
        pkg_list.append(
            {
                "name": pkg.name,
                "version": pkg.version,
                "up_to_date": pkg.version == latest_release.get("version") if latest_release is not None else True,
                "current": current_release,
                "latest": latest_release,
            },
        )
    print(json.dumps(pkg_list, indent=2))  # noqa: T201


__all__ = [
    "print_json",
]
