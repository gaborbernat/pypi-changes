"""Detect and visualize PyPI changes."""

from __future__ import annotations

from ._cli import main
from ._version import __version__

__all__ = [
    "__version__",
    "main",
]
