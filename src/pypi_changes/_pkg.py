from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from packaging.version import Version

if TYPE_CHECKING:
    from datetime import datetime
    from importlib.metadata import PathDistribution
    from pathlib import Path


class Package:
    def __init__(self, dist: PathDistribution, info: dict[str, Any] | Exception | None) -> None:
        self.dist: PathDistribution = dist
        self.info: dict[str, Any] | None = None if isinstance(info, Exception) else info
        self.exc = info if isinstance(info, Exception) else None

    @property
    def last_release_at(self) -> datetime | None:
        if (last_release := self.last_release) is None or last_release.get("synthesized"):
            return None
        return last_release["upload_time_iso_8601"]

    @property
    def last_release(self) -> dict[str, Any] | None:
        if self.info is None or not self.info["releases"]:
            return None
        for version_str, releases in self.info["releases"].items():
            version = Version(version_str)
            if not version.is_devrelease and not version.is_prerelease:
                return releases[0]
        return next(iter(self.info["releases"].values()))[0]

    @property
    def name(self) -> str:
        return self.dist.metadata["Name"]

    @property
    def version(self) -> str:
        return self.dist.version

    @property
    def path(self) -> Path:
        return cast("Path", self.dist._path)  # noqa: SLF001

    @property
    def current_release(self) -> dict[str, Any]:
        if self.info is not None:
            release_info = self.info["releases"].get(self.version)
            if release_info is not None:
                return release_info[0] or {}
        return {}  # return empty version info if not matching

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, path={self.path!r})"


__all__ = [
    "Package",
]
