import os.path

import pytest
from pytest import FixtureRequest


@pytest.fixture(scope="module")
def vcr_cassette_dir(request: FixtureRequest) -> str:
    return os.path.join("tests", "cassettes", request.module.__name__)
