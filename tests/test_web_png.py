from pathlib import Path

import goes_meso_visualizer.web_png
from pystac import ItemCollection


def test_item(data_path: Path) -> None:
    item_collection = ItemCollection.from_file(str(data_path / "colorize.json"))
    item = goes_meso_visualizer.web_png.item(item_collection[0])
    assert "web_png" in item.assets
    assert "visual" not in item.assets
