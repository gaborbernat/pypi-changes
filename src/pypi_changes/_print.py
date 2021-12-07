from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

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
        last_release = pkg.last_release
        if last_release is not None:  # pragma: no branch
            if last_release["version"] != pkg.version and pkg.info is not None:
                for a_version, releases in pkg.info["releases"].items():  # pragma: no branch
                    first_release_at = releases[0]["upload_time_iso_8601"]
                    if a_version == pkg.dist.version and first_release_at is not None:
                        text.append(" ")
                        text.append(naturaltime(now - first_release_at), "green")
                        break
                text.append(f" remote {last_release['version']}", "red")
            if last_release["upload_time_iso_8601"] is not None:  # pragma: no branch
                text.append(" ", "white")
                text.append(naturaltime(now - last_release["upload_time_iso_8601"]), "green")
        tree.add(text)
    rich_print(tree)


__all__ = [
    "print_tree",
]
