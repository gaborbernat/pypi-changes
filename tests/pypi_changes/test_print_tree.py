from __future__ import annotations

import sys
from datetime import UTC, datetime
from importlib.metadata import PathDistribution
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console

from pypi_changes._pkg import Package  # ruff:ignore[import-private-name]  # construct printer input
from pypi_changes._print import print_tree  # ruff:ignore[import-private-name]  # test tree printer

if TYPE_CHECKING:
    import pytest
    from pytest_mock import MockerFixture

    from tests.conftest import Options


def test_print(capsys: pytest.CaptureFixture[str], option_simple: Options, mocker: MockerFixture) -> None:
    mocker.patch("pypi_changes._print.tree.datetime", autospec=True).now.return_value = datetime(
        2021, 11, 6, 10, tzinfo=UTC
    )
    option_simple.python = Path(sys.executable)
    option_simple.sort = "updated"
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


def test_print_alphabetical(capsys: pytest.CaptureFixture[str], option_simple: Options, mocker: MockerFixture) -> None:
    mocker.patch("pypi_changes._print.tree.datetime", autospec=True).now.return_value = datetime(
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


def test_major_bump_bold_style(option_simple: Options, mocker: MockerFixture) -> None:
    mocker.patch("pypi_changes._print.tree.datetime", autospec=True).now.return_value = datetime(
        2021, 11, 6, 10, tzinfo=UTC
    )
    mock_print = mocker.patch("pypi_changes._print.tree.rich_print", autospec=True)
    option_simple.python = Path(sys.executable)
    option_simple.sort = "alphabetic"
    packages = [
        Package(
            mocker.create_autospec(PathDistribution, spec_set=True, version="1.0.0", metadata={"Name": "major-bump"}),
            info={"releases": {"2.0.0": [{"version": "2.0.0", "upload_time_iso_8601": None}]}},
        ),
        Package(
            mocker.create_autospec(PathDistribution, spec_set=True, version="1.0.0", metadata={"Name": "minor-bump"}),
            info={"releases": {"1.1.0": [{"version": "1.1.0", "upload_time_iso_8601": None}]}},
        ),
    ]

    print_tree(packages, option_simple)

    tree = mock_print.call_args[0][0]
    console = Console(record=True, force_terminal=True, width=200)
    console.print(tree)
    html = console.export_html(inline_styles=True)
    major_line = next(line for line in html.splitlines() if "major-bump" in line)
    minor_line = next(line for line in html.splitlines() if "minor-bump" in line)
    major_marker = "font-weight: bold"
    assert major_marker in major_line
    assert major_marker not in minor_line


def test_missing_remote_version_not_bold(option_simple: Options, mocker: MockerFixture) -> None:
    mock_print = mocker.patch("pypi_changes._print.tree.rich_print", autospec=True)
    option_simple.python = Path(sys.executable)
    option_simple.sort = "alphabetic"
    package = Package(
        mocker.create_autospec(PathDistribution, spec_set=True, version="1.0.0", metadata={"Name": "a"}),
        info={"releases": {"2.0.0": [{"upload_time_iso_8601": None}]}},
    )

    print_tree([package], option_simple)

    console = Console(record=True, force_terminal=True, width=200)
    console.print(mock_print.call_args[0][0])
    line = next(line for line in console.export_html(inline_styles=True).splitlines() if "remote" in line)
    assert ("remote None" in line, "font-weight: bold" in line) == (True, False)


def test_invalid_local_version_not_bold(option_simple: Options, mocker: MockerFixture) -> None:
    mock_print = mocker.patch("pypi_changes._print.tree.rich_print", autospec=True)
    option_simple.python = Path(sys.executable)
    option_simple.sort = "alphabetic"
    package = Package(
        mocker.create_autospec(PathDistribution, spec_set=True, version="invalid", metadata={"Name": "a"}),
        info={"releases": {"2.0.0": [{"version": "2.0.0", "upload_time_iso_8601": None}]}},
    )

    print_tree([package], option_simple)

    console = Console(record=True, force_terminal=True, width=200)
    console.print(mock_print.call_args[0][0])
    line = next(line for line in console.export_html(inline_styles=True).splitlines() if "remote" in line)
    assert ("remote 2.0.0" in line, "font-weight: bold" in line) == (True, False)
