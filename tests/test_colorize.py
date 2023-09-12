from pathlib import Path

import goes_meso_visualizer.colorize
from pystac import ItemCollection


def test_item(data_path: Path) -> None:
    item_collection = ItemCollection.from_file(str(data_path / "solarize.json"))
    item = goes_meso_visualizer.colorize.item(item_collection[0])
    assert "visual" in item.assets
    assert "C01_2km" not in item.assets
    assert "C02_2km" not in item.assets
    assert "C03_2km" not in item.assets
    assert "C13_2km" not in item.assets
    assert "solar_altitude" not in item.assets
