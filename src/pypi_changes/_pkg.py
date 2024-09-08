from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from packaging.version import Version

if TYPE_CHECKING:
    from importlib.metadata import PathDistribution


class Package:
    def __init__(self, dist: PathDistribution, info: dict[str, Any] | None | Exception) -> None:
        self.dist: PathDistribution = dist
        self.info: dict[str, Any] | None = None if isinstance(info, Exception) else info
        self.exc = info if isinstance(info, Exception) else None

    @property
    def last_release_at(self) -> datetime:
        last_release = self.last_release
        if last_release is None:
            return datetime.now(timezone.utc)
        return self.last_release["upload_time_iso_8601"]  # type: ignore[no-any-return,index] # Any instead of datetime

    @property
    def last_release(self) -> dict[str, Any] | None:
        if self.info is None or not self.info["releases"]:
            return None
        for version_str, releases in self.info["releases"].items():
            version = Version(version_str)
            if not version.is_devrelease and not version.is_prerelease:
                return releases[0]  # type: ignore[no-any-return]
        return next(iter(self.info["releases"].values()))[0]  # type: ignore[no-any-return]

    @property
    def name(self) -> str:
        return self.dist.metadata["Name"]

    @property
    def version(self) -> str:
        return self.dist.version

    @property
    def path(self) -> Path:
        return cast(Path, self.dist._path)  # noqa: SLF001

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
