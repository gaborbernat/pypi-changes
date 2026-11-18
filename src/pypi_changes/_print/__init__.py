"""Output formats of the package list."""

from __future__ import annotations

__lazy_modules__ = [
    f"{__spec__.parent}.json",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
    f"{__spec__.parent}.requirements",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
    f"{__spec__.parent}.tree",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
]

from typing import TYPE_CHECKING

from .json import print_json
from .requirements import print_requirements
from .tree import print_tree

if TYPE_CHECKING:
    from pypi_changes import Options as Options
    from pypi_changes import Package as Package
    from pypi_changes import Release as Release

__all__ = [
    "print_json",
    "print_requirements",
    "print_tree",
]
