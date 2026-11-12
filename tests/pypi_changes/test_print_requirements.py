from __future__ import annotations

import sys
from datetime import UTC, datetime
from importlib.metadata import PathDistribution
from pathlib import Path
from typing import TYPE_CHECKING

from pypi_changes._pkg import Package  # ruff:ignore[import-private-name]  # construct printer input
from pypi_changes._print import print_requirements  # ruff:ignore[import-private-name]  # test requirements printer

if TYPE_CHECKING:
    import pytest
    from pytest_mock import MockerFixture

    from tests.conftest import Options


def test_print_requirements(capsys: pytest.CaptureFixture[str], option_simple: Options, mocker: MockerFixture) -> None:
    mocker.patch("pypi_changes._print.requirements.datetime", autospec=True).now.return_value = datetime(
        2021, 11, 6, 10, tzinfo=UTC
    )
    option_simple.python = Path(sys.executable)
    option_simple.sort = "alphabetic"
    packages = [
        Package(
            mocker.create_autospec(PathDistribution, spec_set=True, version=v_l, metadata={"Name": n}),
            info={"releases": {v_u: [{"version": v_u, "upload_time_iso_8601": t}]}},
        )
        for n, v_l, v_u, t in [
            ("a", "1", "2", datetime(2021, 10, 5, 10, tzinfo=UTC)),
            ("b", "3", "3", datetime(2021, 11, 5, 10, tzinfo=UTC)),
            ("d", "1", "1", None),
            ("c", "1", "2", None),
        ]
    ]

    print_requirements(packages, option_simple)

    out, err = capsys.readouterr()
    assert not err
    assert out.splitlines() == ["a==2", "c==2"]


def test_print_requirements_no_outdated(
    capsys: pytest.CaptureFixture[str], option_simple: Options, mocker: MockerFixture
) -> None:
    mocker.patch("pypi_changes._print.requirements.datetime", autospec=True).now.return_value = datetime(
        2021, 11, 6, 10, tzinfo=UTC
    )
    option_simple.python = Path(sys.executable)
    option_simple.sort = "alphabetic"
    packages = [
        Package(
            mocker.create_autospec(PathDistribution, spec_set=True, version="1", metadata={"Name": "a"}),
            info={"releases": {"1": [{"version": "1", "upload_time_iso_8601": datetime(2021, 10, 5, 10, tzinfo=UTC)}]}},
        ),
    ]

    print_requirements(packages, option_simple)

    out, err = capsys.readouterr()
    assert not err
    assert not out
