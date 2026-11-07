from __future__ import annotations


def test_version() -> None:
    from pypi_changes import __version__  # ruff:ignore[import-outside-top-level]  # the import is the check

    assert __version__
