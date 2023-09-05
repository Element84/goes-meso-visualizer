import pytest
from goes_meso_visualizer import constants, search, shapes


@pytest.mark.vcr
def test_goes() -> None:
    items = search.goes(
        shapes.ep092023_best_track(),
        start=constants.EP092023_FORMED,
        end=constants.EP092023_DISSIPATED,
        max_items=1,
    )
    assert len(items) == 1
