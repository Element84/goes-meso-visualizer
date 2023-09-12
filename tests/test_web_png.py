from typing import Callable

import goes_meso_visualizer.web_png
from pystac import ItemCollection


def test_item(load_item_collection: Callable[[str], ItemCollection]) -> None:
    item_collection = load_item_collection("colorize.json")
    item = goes_meso_visualizer.web_png.item(item_collection[0])
    assert "web_png" in item.assets
    assert "visual" not in item.assets
