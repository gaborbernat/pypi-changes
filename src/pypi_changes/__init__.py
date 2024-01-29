"""Detect and visualize PyPI changes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._cli import parse_cli_arguments
from ._distributions import collect_distributions
from ._info import pypi_info
from ._print.json import print_json
from ._print.tree import print_tree
from ._version import version

if TYPE_CHECKING:
    from collections.abc import Sequence

#: semantic version of the package
__version__ = version


def main(args: Sequence[str] | None = None) -> int:
    """
    Execute the entry point.

    :param args: CLI arguments
    :return: exit code
    """
    options = parse_cli_arguments(args)
    distributions = collect_distributions(options)
    info = pypi_info(distributions, options)

    if options.output == "tree":
        print_tree(info, options)
    else:  # output == "json"
        print_json(info, options)
    return 0


__all__ = [
    "__version__",
    "main",
]
