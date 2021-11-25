from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Iterable

from humanize import naturaltime
from rich import print as rich_print
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree

from ._cli import Options
from ._pkg import Package


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


def print_tree(distributions: Iterable[Package], options: Options) -> None:
    now = datetime.now(timezone.utc)
    tree = Tree(f"🐍 Distributions within {escape(str(options.python))}", guide_style="cyan")
    for pkg in get_sorted_pkg_list(distributions, options, now):
        text = Text(pkg.name, "yellow")
        text.stylize(f"link https://pypi.org/project/{pkg.name}/#history")
        text.append(" ", "white")
        text.append(pkg.version, "blue")

        current_release = pkg.current_release
        current_release_at = current_release.get("upload_time_iso_8601")
        last_release = pkg.last_release or {}
        last_release_at = pkg.last_release_at

        if current_release_at is not None:
            text.append(" ")  # pragma: no cover
            text.append(naturaltime(now - current_release_at), "green")  # pragma: no cover
        if pkg.version != last_release.get("version"):
            text.append(f" remote {last_release.get('version')}", "red")
            if last_release_at is not None:  # pragma: no branch
                text.append(" ", "white")
                text.append(naturaltime(now - last_release_at), "green")
        tree.add(text)
    rich_print(tree)


def release_info(release: dict[str, Any] | None, now: datetime) -> dict[str, Any]:
    if release is None:
        return {}
    release_at = release.get("upload_time_iso_8601")
    release_since = naturaltime(now - release_at) if release_at else None
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
            }
        )
    print(json.dumps(pkg_list, indent=2))


__all__ = [
    "print_tree",
]
