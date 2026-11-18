from __future__ import annotations

__lazy_modules__ = [
    "datetime",
    f"{__spec__.parent}._sort",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
]

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from ._sort import get_sorted_pkg_list

if TYPE_CHECKING:
    from collections.abc import Iterable

    from . import Options, Package


def print_requirements(distributions: Iterable[Package], options: Options) -> None:
    for pkg in get_sorted_pkg_list(distributions, options, datetime.now(UTC)):
        if (remote_version := (pkg.last_release or {}).get("version")) and pkg.version != remote_version:
            print(f"{pkg.name}=={remote_version}")  # ruff:ignore[print]  # the requirement lines are the output


__all__ = [
    "print_requirements",
]
