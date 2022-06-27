from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .._cli import Options
from .._pkg import Package


class Reversor:
    def __init__(self, obj: str) -> None:
        self.obj = obj

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Reversor) and other.obj == self.obj

    def __lt__(self, other: Reversor) -> bool:
        return other.obj < self.obj


def get_sorted_pkg_list(distributions: Iterable[Package], options: Options, now: datetime) -> Iterable[Package]:
    if options.sort in ["a", "alphabetic"]:
        return sorted(distributions, key=lambda v: v.name.lower())
    return sorted(distributions, key=lambda v: (v.last_release_at or now, Reversor(v.name)), reverse=True)
