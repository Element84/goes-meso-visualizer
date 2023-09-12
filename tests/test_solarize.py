from typing import Callable

import goes_meso_visualizer.solarize
from pystac import ItemCollection


def test_item(load_item_collection: Callable[[str], ItemCollection]) -> None:
    item_collection = load_item_collection("download.json")
    item = goes_meso_visualizer.solarize.item(item_collection[0])
    assert "solar_altitude" in item.assets
