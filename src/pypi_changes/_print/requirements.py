from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from . import get_sorted_pkg_list

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pypi_changes._cli import Options
    from pypi_changes._pkg import Package


def print_requirements(distributions: Iterable[Package], options: Options) -> None:
    now = datetime.now(timezone.utc)
    for pkg in get_sorted_pkg_list(distributions, options, now):
        last_release = pkg.last_release or {}
        if (remote_version := last_release.get("version")) and pkg.version != remote_version:
            print(f"{pkg.name}=={remote_version}")  # noqa: T201


__all__ = [
    "print_requirements",
]
