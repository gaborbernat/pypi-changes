"""Detect and visualize PyPI changes."""

from __future__ import annotations

from typing import TYPE_CHECKING  # simplint: ignore[init-module-content]  # type-only re-exports

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
