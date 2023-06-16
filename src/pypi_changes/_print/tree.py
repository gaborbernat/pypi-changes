from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from humanize import naturaldelta
from rich import print as rich_print
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree

from . import get_sorted_pkg_list

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pypi_changes._cli import Options
    from pypi_changes._pkg import Package


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
            text.append(naturaldelta(now - current_release_at), "green")  # pragma: no cover
        if pkg.version != last_release.get("version"):
            text.append(f" remote {last_release.get('version')}", "red")
            if last_release_at is not None:  # pragma: no branch
                text.append(" ", "white")
                text.append(naturaldelta(now - last_release_at), "green")
        tree.add(text)
    rich_print(tree)


__all__ = [
    "print_tree",
]
