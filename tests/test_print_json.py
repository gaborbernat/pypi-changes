from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import create_autospec

from pypi_changes._pkg import Package
from pypi_changes._print.json import print_json, release_info
from tests import PathDistribution

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from pytest_mock import MockerFixture

    from pypi_changes._cli import Options


def test_print_json(capsys: CaptureFixture[str], option_simple: Options, mocker: MockerFixture) -> None:
    mocked_datetime = mocker.patch("pypi_changes._print.json.datetime")
    mocked_datetime.now.return_value = datetime(2021, 11, 6, 10, tzinfo=timezone.utc)
    option_simple.python = Path(sys.executable)
    option_simple.sort = "unsorted"
    packages = [
        Package(
            create_autospec(PathDistribution, spec_set=True, version=v_cur, metadata={"Name": n}),
            info={
                "releases": {
                    v_last: [{"version": v_last, "upload_time_iso_8601": t_last}],
                    v_cur: [{"version": v_cur, "upload_time_iso_8601": t_cur}],
                },
            },
        )
        for n, (v_last, t_last), (v_cur, t_cur) in [
            (
                "a",
                ("2", datetime(2021, 10, 5, 10, tzinfo=timezone.utc)),
                ("1", datetime(2020, 3, 8, 10, tzinfo=timezone.utc)),
            ),
            (
                "b",
                ("2", None),
                ("1", None),
            ),
        ]
    ]

    print_json(packages, option_simple)

    out, err = capsys.readouterr()
    assert not err
    output = [i.strip() for i in out.splitlines()]
    parsed_output = json.loads("".join(output))
    assert parsed_output == [
        {
            "name": "b",
            "version": "1",
            "up_to_date": False,
            "current": {"version": "1", "date": None, "since": None},
            "latest": {"version": "2", "date": None, "since": None},
        },
        {
            "name": "a",
            "version": "1",
            "up_to_date": False,
            "current": {
                "version": "1",
                "date": "2020-03-08T10:00:00+00:00",
                "since": "1 year, 7 months",
            },
            "latest": {
                "version": "2",
                "date": "2021-10-05T10:00:00+00:00",
                "since": "a month",
            },
        },
    ]


def test_release_info_no_release() -> None:
    result = release_info(None, datetime.now(timezone.utc))

    assert result == {}
