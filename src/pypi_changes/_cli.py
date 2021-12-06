from __future__ import annotations

from argparse import Action, ArgumentDefaultsHelpFormatter, ArgumentError, ArgumentParser, Namespace
from pathlib import Path
from typing import Sequence

from platformdirs import user_cache_path

from ._version import version


class Options(Namespace):
    python: Path
    jobs: int
    cache_path: Path
    cache_duration: int
    sort: str


def parse_cli_arguments(args: Sequence[str] | None = None) -> Options:
    parser = _define_cli_arguments()
    options = Options()
    parser.parse_args(args, options)
    return options


def _define_cli_arguments() -> ArgumentParser:
    epilog = f"running {version} at {Path(__file__).parent}"
    parser = ArgumentParser(prog="pypi-changes", formatter_class=_HelpFormatter, epilog=epilog)

    parallel_help = "maximum number of parallel requests when loading distribution information from PyPI"
    parser.add_argument("--jobs", "-j", default=10, type=int, help=parallel_help, metavar="COUNT")

    path = user_cache_path(appname="pypi_changes", appauthor="gaborbernat", version=version) / "requests.sqlite"
    parser.add_argument(
        "--cache-path",
        "-c",
        default=path,
        type=Path,
        help="requests are cached to disk to this sqlite file",
        metavar="PATH",
        dest="cache_path",
    )
    cache_help = "seconds how long requests should be cached (pass 0 to bypass the cache, -1 to cache forever)"
    parser.add_argument("--cache-duration", "-d", default=3600, type=int, help=cache_help, metavar="SEC")

    sort = parser.add_argument_group(description="Result sorting method")
    sort.add_argument(
        "--alphabetic",
        "-a",
        help="sort output alphabetically",
        action="store_const",
        dest="sort",
        const="alphabetic",  # noqa: SC200
    )
    sort.add_argument(
        "--updated",
        "-u",
        help="sort by modification date",
        action="store_const",
        dest="sort",
        const="updated",  # noqa: SC200
        default="updated",
    )

    parser.add_argument("python", help="python interpreter to inspect", metavar="PYTHON_EXE", action=_Python)

    return parser


class _Python(Action):
    def __call__(
        self,
        parser: ArgumentParser,  # noqa: U100
        namespace: Namespace,  # noqa: U100
        values: str | Sequence[str] | None,
        option_string: str | None = None,  # noqa: U100
    ) -> None:
        assert isinstance(values, str)
        path = Path(values).absolute()
        if not path.exists():
            raise ArgumentError(self, f"path {path} does not exist")
        setattr(namespace, self.dest, path)


class _HelpFormatter(ArgumentDefaultsHelpFormatter):
    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=35, width=190)


__all__ = [
    "Options",
    "parse_cli_arguments",
]
