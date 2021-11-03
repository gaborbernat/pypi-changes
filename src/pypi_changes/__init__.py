from __future__ import annotations

import json
import re
import ssl
import sys
from argparse import Action, ArgumentDefaultsHelpFormatter, ArgumentError, ArgumentParser, Namespace
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from http import HTTPStatus
from operator import attrgetter
from pathlib import Path
from subprocess import check_output
from typing import Any, Generator, Iterable, Sequence
from urllib.error import HTTPError
from urllib.request import urlopen

from humanize import naturaltime
from rich import print as rich_print
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree

if sys.version_info >= (3, 8):
    from functools import cached_property
    from importlib.metadata import Distribution, PathDistribution
else:
    from backports.cached_property import cached_property
    from importlib_metadata import Distribution, PathDistribution

from ._version import version

#: semantic version of the package
__version__ = version

PACKAGE_REGEX = re.compile(r"^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])(\.egg-info|\.dist-info)$", flags=re.IGNORECASE)


class Options(Namespace):
    python: Path
    pypi_parallel: int


def one_info(dist: Distribution) -> dict[str, Any] | None:
    # the most accurate is to ask PyPi - e.g. https://pypi.org/pypi/pip/json,
    # see https://warehouse.pypa.io/api-reference/json/ for more details
    content, url = None, f"https://pypi.org/pypi/{dist.metadata['Name']}/json"
    # fallback to non verified HTTPS (the information we request is not sensitive, so fallback)
    for context in (None, ssl._create_unverified_context()):
        try:
            with urlopen(url, context=context) as file_handler:
                content = json.load(file_handler)
        except HTTPError as exception:
            if exception.code == HTTPStatus.NOT_FOUND:
                return None
        break
    return content


class Package:
    def __init__(self, dist: PathDistribution, info: dict[str, Any] | None | Exception) -> None:
        self.dist: PathDistribution = dist
        self.info: dict[str, Any] | None = None if isinstance(info, Exception) else info
        self.exc = info if isinstance(info, Exception) else None

    @cached_property
    def releases(self) -> list[tuple[str, list[dict[str, Any]]]] | None:
        if self.info is None:
            return None
        releases = self.info["releases"]
        for a_version in releases.values():
            for release in a_version:
                raw = release["upload_time_iso_8601"]
                release["upload_time_iso_8601"] = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        items = releases.items()
        result = sorted(
            items,
            key=lambda v: max(i["upload_time_iso_8601"] for i in v[1])  # type: ignore # doesn't know its datetime
            if v[1]
            else datetime(1970, 1, 1, tzinfo=timezone.utc),
        )
        return result

    @property
    def last_release_at(self) -> datetime:
        return (  # type: ignore
            datetime.now(timezone.utc)
            if self.releases is None
            else (
                max(i["upload_time_iso_8601"] for i in self.releases[-1][1])
                if self.releases[-1][1]
                else datetime(1970, 1, 1, tzinfo=timezone.utc)
            )
        )

    @property
    def name(self) -> str:
        return self.dist.metadata["Name"]  # type: ignore

    @property
    def version(self) -> str:
        return self.dist.version

    def path(self) -> Path:
        return self.dist._path  # type: ignore # it exists


def pypi_info(distributions: Iterable[PathDistribution]) -> Generator[Package, None, None]:
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(one_info, dist): dist for dist in distributions}
        for future in as_completed(future_to_url):
            dist = future_to_url[future]
            try:
                result: Exception | dict[str, Any] | None = future.result()
            except Exception as exc:
                result = exc
            yield Package(dist, result)


def iter_distributions(paths: Iterable[Path]) -> Generator[PathDistribution, None, None]:
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
            match = PACKAGE_REGEX.match(candidate.name)
            if match:
                dist = Distribution.at(candidate)
                name = dist.metadata["Name"]
                if name not in found:
                    found.add(name)
                    yield dist


def parse_cli_arguments(args: Sequence[str] | None = None) -> Options:
    class HelpFormatter(ArgumentDefaultsHelpFormatter):
        def __init__(self, prog: str) -> None:
            super().__init__(prog, max_help_position=35, width=190)

    class PythonInterpreter(Action):
        def __call__(
            self,
            parser: ArgumentParser,
            namespace: Namespace,
            values: str | Sequence[str] | None,
            option_string: str | None = None,
        ) -> None:
            assert isinstance(values, str)
            path = Path(values).absolute()
            if not path.exists():
                raise ArgumentError(self, f"path {path} does not exist")
            setattr(namespace, self.dest, path)

    parser = ArgumentParser(prog="pypi-changes", formatter_class=HelpFormatter)
    parser.add_argument(
        "-p", "--python", help="python interpreter to inspect", required=True, metavar="PATH", action=PythonInterpreter
    )
    parser.add_argument("--parallel", default=10, type=int, help="maximum parallelization when query PyPI")
    opts = Options()
    parser.parse_args(args, opts)
    return opts


def _print_tree(distributions: Iterable[Package], opts: Options) -> None:
    now = datetime.now(timezone.utc)
    tree = Tree(f"🐍 [link file://{opts.python}]{escape(str(opts.python))}", guide_style="cyan")
    for pkg in sorted(distributions, key=attrgetter("last_release_at"), reverse=True):
        text = Text(pkg.name, "yellow")
        text.stylize(f"link file://{str(pkg.path)}")
        text.append(" ", "white")
        text.append(pkg.version, "blue")
        if pkg.releases:
            last_release = pkg.releases[-1]
            if last_release[0] != pkg.version:
                for a_version, releases in pkg.releases:
                    if a_version == pkg.dist.version:
                        text.append(" ")
                        text.append(naturaltime(now - releases[0]["upload_time_iso_8601"]), "green")
                        break
                text.append(f" remote {last_release[0]}", "red")
            if last_release[1]:
                text.append(" ", "white")
                text.append(naturaltime(now - last_release[1][0]["upload_time_iso_8601"]), "green")
        tree.add(text)
    rich_print(tree)


def main(args: Sequence[str] | None = None) -> int:
    opts = parse_cli_arguments(args)
    cmd = [str(opts.python), "-c", "import sys, json; print(json.dumps(sys.path))"]
    data = pypi_info(iter_distributions(Path(i) for i in json.loads(check_output(cmd, universal_newlines=True))))
    _print_tree(data, opts)
    return 0


__all__ = [
    "__version__",
    "main",
]
