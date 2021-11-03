from __future__ import annotations

from typing import Sequence

from ._cli import parse_cli_arguments
from ._distributions import collect_distributions
from ._info import pypi_info
from ._print import print_tree
from ._version import version

#: semantic version of the package
__version__ = version


def main(args: Sequence[str] | None = None) -> int:
    options = parse_cli_arguments(args)
    distributions = collect_distributions(options)
    info = pypi_info(distributions, options)
    print_tree(info, options)
    return 0


__all__ = [
    "__version__",
    "main",
]
