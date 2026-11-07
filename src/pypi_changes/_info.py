from __future__ import annotations

import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import ExitStack, contextmanager
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Final, TypedDict

from packaging.version import InvalidVersion, Version
from pypi_simple import PyPISimple
from requests_cache import CachedSession
from rich.progress import BarColumn, Progress, Task, TextColumn, TimeRemainingColumn
from rich.text import Text

from ._pkg import Package

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence
    from importlib.metadata import PathDistribution

    from requests import Session

    from ._cli import Options
    from ._pkg import Project, Release

PYPI_INDEX: Final[str] = "https://pypi.org/simple"


def pypi_info(distributions: Sequence[PathDistribution], options: Options) -> Generator[Package, None, None]:
    with ExitStack() as stack:
        enter = stack.enter_context
        session = enter(CachedSession(str(options.cache_path), backend="sqlite", expire_after=options.cache_duration))
        session.cache.delete(expired=True)  # cleanup old entries

        client = enter(_pypi_client(session))

        progress = Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            TextColumn("[bold magenta] {task.completed}/{task.total}"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            _SpeedColumn(),
            TimeRemainingColumn(),
            transient=True,
        )
        enter(progress)
        task = progress.add_task("[red]Acquire release information", total=len(distributions))

        executor = enter(ThreadPoolExecutor(max_workers=options.jobs, thread_name_prefix="version-getter"))
        future_to_url = {executor.submit(_one_info, client, session, dist): dist for dist in distributions}
        for future in as_completed(future_to_url):
            dist = future_to_url[future]
            progress.update(task, advance=1)
            try:
                result: Exception | Project | None = future.result()
            except Exception as exc:  # ruff:ignore[blind-except]  # the error is kept on its package
                result = exc
            yield Package(dist, result)


@contextmanager
def _pypi_client(session: Session) -> Generator[PyPISimple | None, None, None]:
    if (url := os.environ.get("PIP_INDEX_URL")) is not None and url.lstrip("/") != PYPI_INDEX:
        with PyPISimple(endpoint=url, session=session) as client:
            yield client
    else:
        yield None


class _SpeedColumn(TextColumn):
    def __init__(self) -> None:
        super().__init__("[bold cyan]")

    def render(self, task: Task) -> Text:  # ruff:ignore[no-self-use]  # rich's column API renders per instance
        if task.speed is None:
            return Text("no speed")
        return Text(f"{task.speed:.3f} steps/s")


def _one_info(pypi_client: PyPISimple | None, session: CachedSession, dist: PathDistribution) -> Project | None:
    name: str = dist.metadata["Name"]
    result = _load_from_pypi_json_api(name, session)
    if pypi_client is not None:
        result["releases"] = _merge_with_index_server(name, pypi_client, result["releases"])
    return result


def _load_from_pypi_json_api(name: str, session: CachedSession) -> Project:
    # ask PyPi - e.g. https://pypi.org/pypi/pip/json, see https://warehouse.pypa.io/api-reference/json/ for more details
    response = session.get(f"https://pypi.org/pypi/{name}/json")
    raw: _RawProject = response.json() if response.ok else {"releases": {}}

    # normalize response
    prev_release_at = datetime.now(UTC)
    releases: dict[str, list[Release]] = {}
    for a_version, artifact_release in sorted(raw["releases"].items(), reverse=True):
        if artifact_release:  # enrich into releases version and transform upload time to python datetime
            releases[a_version] = [
                {
                    **release,
                    "version": a_version,
                    "upload_time_iso_8601": datetime.fromisoformat(release["upload_time_iso_8601"]),
                }
                for release in artifact_release
            ]
            prev_release_at = datetime.fromisoformat(artifact_release[0]["upload_time_iso_8601"])
        else:  # if no releases make up a release time and enrich version
            prev_release_at -= timedelta(seconds=1)
            releases[a_version] = [
                {
                    "packagetype": "sdist",
                    "version": a_version,
                    "upload_time_iso_8601": prev_release_at,
                    "synthesized": True,
                },
            ]
    return {"releases": dict(sorted(releases.items(), key=_sort_by_version_release, reverse=True))}


def _sort_by_version_release(value: tuple[str, list[Release]]) -> tuple[Version, datetime | None]:
    try:
        version = Version(value[0])
    except InvalidVersion:
        version = Version("0.0.1")
    return version, value[1][0]["upload_time_iso_8601"]


def _merge_with_index_server(
    name: str,
    pypi_client: PyPISimple,
    releases: dict[str, list[Release]],
) -> dict[str, list[Release]]:
    index_info = pypi_client.get_project_page(name)
    index_releases: defaultdict[str, list[Release]] = defaultdict(list)
    for pkg in index_info.packages:
        if pkg.version is not None:  # some Artifactory might not set this for .egg-info uploads, ignore those
            release: Release = {"packagetype": pkg.package_type, "version": pkg.version, "upload_time_iso_8601": None}
            index_releases[pkg.version].append(release)

    if missing := {ver: values for ver, values in index_releases.items() if ver not in releases}:
        missing.update(releases)
        return dict(sorted(missing.items(), key=_sort_by_version_release, reverse=True))
    return releases


class _RawRelease(TypedDict):
    upload_time_iso_8601: str


class _RawProject(TypedDict):
    releases: dict[str, list[_RawRelease]]


__all__ = [
    "pypi_info",
]
