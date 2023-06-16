from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import create_autospec

from pypi_changes._pkg import Package
from pypi_changes._print.tree import print_tree
from tests import PathDistribution

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from pytest_mock import MockerFixture

    from pypi_changes._cli import Options


def test_print(capsys: CaptureFixture[str], option_simple: Options, mocker: MockerFixture) -> None:
    mocked_datetime = mocker.patch("pypi_changes._print.tree.datetime")
    mocked_datetime.now.return_value = datetime(2021, 11, 6, 10, tzinfo=timezone.utc)
    option_simple.python = Path(sys.executable)
    option_simple.sort = "updated"
    packages = [
        Package(
            create_autospec(PathDistribution, spec_set=True, version=v_l, metadata={"Name": n}),
            info={"releases": {v_u: [{"version": v_u, "upload_time_iso_8601": t}]}},
        )
        for n, v_l, v_u, t in [
            ("a", "1", "2", datetime(2021, 10, 5, 10, tzinfo=timezone.utc)),
            ("b", "3", "3", datetime(2021, 11, 5, 10, tzinfo=timezone.utc)),
            ("d", "1", "1", None),
            ("c", "1", "2", None),
        ]
    ]

    print_tree(packages, option_simple)

    out, err = capsys.readouterr()
    assert not err
    output = [i.strip() for i in out.splitlines()]
    assert output[0].startswith("🐍 Distributions within")
    assert output[1] == sys.executable or output[0].endswith(sys.executable)
    assert output[-4:] == [
        "├── c 1 remote 2",
        "├── d 1",
        "├── b 3 a day",
        "└── a 1 remote 2 a month",
    ]


def test_print_alphabetical(capsys: CaptureFixture[str], option_simple: Options, mocker: MockerFixture) -> None:
    mocked_datetime = mocker.patch("pypi_changes._print.tree.datetime")
    mocked_datetime.now.return_value = datetime(2021, 11, 6, 10, tzinfo=timezone.utc)
    option_simple.python = Path(sys.executable)
    option_simple.sort = "alphabetic"
    packages = [
        Package(
            create_autospec(PathDistribution, spec_set=True, version=v_l, metadata={"Name": n}),
            info={"releases": {v_u: [{"version": v_u, "upload_time_iso_8601": t}]}},
        )
        for n, v_l, v_u, t in [
            ("a", "1", "2", datetime(2021, 10, 5, 10, tzinfo=timezone.utc)),
            ("b", "3", "3", datetime(2021, 11, 5, 10, tzinfo=timezone.utc)),
            ("d", "1", "1", None),
            ("c", "1", "2", None),
        ]
    ]

    print_tree(packages, option_simple)

    out, err = capsys.readouterr()
    assert not err
    output = [i.strip() for i in out.splitlines()]
    assert output[0].startswith("🐍 Distributions within")
    assert output[1] == sys.executable or output[0].endswith(sys.executable)
    assert output[-4:] == [
        "├── a 1 remote 2 a month",
        "├── b 3 a day",
        "├── c 1 remote 2",
        "└── d 1",
    ]
