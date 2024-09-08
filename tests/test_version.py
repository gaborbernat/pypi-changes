from __future__ import annotations


def test_version() -> None:
    from pypi_changes import __version__  # noqa: PLC0415

    assert __version__
