from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable
from unittest.mock import MagicMock

if sys.version_info >= (3, 8):  # pragma: no cover (py38+)
    from importlib.metadata import PathDistribution
else:  # pragma: no cover (<py38)
    from importlib_metadata import PathDistribution

MakeDist = Callable[[Path, str, str], MagicMock]

__all__ = [
    "PathDistribution",
    "MakeDist",
]
