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


def print_tree(distributions: Iterable[Package], options: Options) -> None:
    now = datetime.now(timezone.utc)
    tree = Tree(f"🐍 Distributions within {escape(str(options.python.parent))}", guide_style="cyan")
    for pkg in sorted(distributions, key=lambda v: v.last_release_at or now, reverse=True):
        text = Text(pkg.name, "yellow")
        text.stylize(f"link https://pypi.org/project/{pkg.name}/#history")
        text.append(" ", "white")
        text.append(pkg.version, "blue")
        last_release = pkg.last_release
        if last_release is not None:
            if last_release["version"] != pkg.version and pkg.info is not None:
                for a_version, releases in pkg.info["releases"].items():
                    if a_version == pkg.dist.version and releases[0]["upload_time_iso_8601"] is not None:
                        text.append(" ")
                        text.append(naturaltime(now - releases[0]["upload_time_iso_8601"]), "green")
                        break
                text.append(f" remote {last_release['version']}", "red")
            if last_release["upload_time_iso_8601"] is not None:
                text.append(" ", "white")
                text.append(naturaltime(now - last_release["upload_time_iso_8601"]), "green")
        tree.add(text)
    rich_print(tree)


__all__ = [
    "print_tree",
]
