"""Detect and visualize PyPI changes."""

from __future__ import annotations

__lazy_modules__ = [
    f"{__spec__.parent}._cli",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
    f"{__spec__.parent}._version",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
]

from typing import TYPE_CHECKING

from ._cli import main
from ._version import __version__

if TYPE_CHECKING:
    from ._cli import Options as Options
    from ._pkg import Package as Package
    from ._pkg import Release as Release

__all__ = [
    "__version__",
    "main",
]
