from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from subprocess import check_output
from typing import Generator, Iterable

from rich.console import Console

from ._cli import Options

if sys.version_info >= (3, 8):
    from importlib.metadata import Distribution, PathDistribution
else:
    from importlib_metadata import Distribution, PathDistribution


_PKG_REGEX = re.compile(r"^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])(\.egg-info|\.dist-info)$", flags=re.IGNORECASE)


def collect_distributions(options: Options) -> list[PathDistribution]:
    distributions: list[PathDistribution] = []
    with Console().status("Discovering distributions") as status:
        paths = _get_py_info(str(options.python))
        for dist in _iter_distributions(paths):
            status.update(f"Discovering distributions {len(distributions)}")
            distributions.append(dist)
    return distributions


def _get_py_info(python: str) -> list[Path]:
    cmd = [python, "-c", "import sys, json; print(json.dumps(sys.path))"]
    paths = [Path(i) for i in json.loads(check_output(cmd, universal_newlines=True))]
    return paths


def _iter_distributions(paths: Iterable[Path]) -> Generator[PathDistribution, None, None]:
    found: set[str] = set()
    done_paths: set[Path] = set()
    for path in paths:
        if not path.exists():
            continue
        path = path.resolve()
        if path in done_paths:
            continue
        done_paths.add(path)
        for candidate in path.iterdir():
            if not candidate.is_dir():
                continue
            match = _PKG_REGEX.match(candidate.name)
            if match:
                dist = Distribution.at(candidate)
                name = dist.metadata["Name"]
                if name not in found:
                    found.add(name)
                    yield dist


__all__ = [
    "collect_distributions",
]
