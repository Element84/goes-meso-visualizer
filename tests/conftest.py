import os.path
from typing import Any

import pytest
from pytest import Config, FixtureRequest, Parser


@pytest.fixture(scope="module")
def vcr_cassette_dir(request: FixtureRequest) -> str:
    return os.path.join("tests", "cassettes", request.module.__name__)


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--slow",
        action="store_true",
        default=False,
        help="run tests that are slow",
    )


def pytest_configure(config: Config) -> None:
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow" "and disables them by default (enable with --slow)",
    )


def pytest_collection_modifyitems(config: Config, items: Any) -> None:
    if config.getoption("--slow"):
        return
    skip_network_access = pytest.mark.skip(reason="need --slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_network_access)
