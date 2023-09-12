import datetime
from datetime import timezone

import pytest
from goes_meso_visualizer import search, shapes


@pytest.mark.vcr
def test_goes() -> None:
    items = search.goes(
        shapes.ep092023_best_track(),
        start=datetime.datetime(2023, 8, 16, tzinfo=timezone.utc),
        end=datetime.datetime(2023, 8, 21, tzinfo=timezone.utc),
        max_items=1,
    )
    assert len(items) == 1
    assert isinstance(items.extra_fields["intersects"], dict)
    intersects = items.extra_fields["intersects"]
    assert intersects["type"] == "MultiLineString"
    assert len(intersects["coordinates"]) == 9
