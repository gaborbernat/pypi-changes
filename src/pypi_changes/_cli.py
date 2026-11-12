from __future__ import annotations

import shutil
from argparse import Action, ArgumentDefaultsHelpFormatter, ArgumentError, ArgumentParser, Namespace
from pathlib import Path
from typing import TYPE_CHECKING

from platformdirs import user_cache_path

from ._distributions import collect_distributions
from ._info import pypi_info
from ._print import print_json, print_requirements, print_tree
from ._version import version

if TYPE_CHECKING:
    from collections.abc import Sequence


def main(args: Sequence[str] | None = None) -> int:
    """
    Execute the entry point.

    :param args: CLI arguments
    :returns: exit code
    """
    options = parse_cli_arguments(args)
    info = pypi_info(collect_distributions(options), options)

    if options.output == "tree":
        print_tree(info, options)
    elif options.output == "json":
        print_json(info, options)
    else:  # output == "requirements"
        print_requirements(info, options)
    return 0


def parse_cli_arguments(args: Sequence[str] | None) -> Options:
    parser = _define_cli_arguments()
    options = Options()
    parser.parse_args(args, options)
    if options.python is None:
        if (resolved := shutil.which("python")) is None:
            parser.error("no python interpreter found on PATH, provide PYTHON_EXE explicitly")
        options.python = Path(resolved).absolute()
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

    parser.add_argument(
        "--sort",
        "-s",
        help="sorting method",
        choices=["a", "alphabetic", "u", "updated"],
        default="updated",
        dest="sort",
        const="updated",
        nargs="?",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Choose output format",
        choices=["tree", "json", "requirements"],
        default="tree",
        dest="output",
    )

    parser.add_argument(
        "python",
        help="python interpreter to inspect (default: python on PATH)",
        metavar="PYTHON_EXE",
        action=_Python,
        nargs="?",
        default=None,
    )

    return parser


class _HelpFormatter(ArgumentDefaultsHelpFormatter):
    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=35, width=190)


class _Python(Action):
    def __call__(
        self,
        parser: ArgumentParser,  # ruff:ignore[unused-method-argument]  # argparse passes every action its parser
        namespace: Namespace,
        values: str | Sequence[str] | None,
        option_string: str | None = None,  # ruff:ignore[unused-method-argument]  # unused for a positional argument
    ) -> None:
        if values is None:
            return
        assert isinstance(values, str)  # ruff:ignore[assert]  # nargs="?" yields a single string here
        path = Path(values).absolute()
        if not path.exists():
            raise ArgumentError(self, f"path {path} does not exist")
        setattr(namespace, self.dest, path)


class Options(Namespace):
    python: Path
    jobs: int
    cache_path: Path
    cache_duration: int
    sort: str


__all__ = [
    "Options",
    "main",
    "parse_cli_arguments",
]
