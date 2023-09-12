from pathlib import Path

import goes_meso_visualizer.solarize
from pystac import ItemCollection


def test_item(data_path: Path) -> None:
    item_collection = ItemCollection.from_file(str(data_path / "download.json"))
    item = goes_meso_visualizer.solarize.item(item_collection[0])
    assert "solar_altitude" in item.assets
