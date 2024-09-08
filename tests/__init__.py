from __future__ import annotations

from collections.abc import Callable
from importlib.metadata import PathDistribution
from pathlib import Path
from unittest.mock import MagicMock

MakeDist = Callable[[Path, str, str], MagicMock]

__all__ = [
    "MakeDist",
    "PathDistribution",
]
