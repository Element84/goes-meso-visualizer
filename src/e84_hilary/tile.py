import subprocess
from pathlib import Path

from pystac import Asset, Item


def item(item: Item) -> Item:
    infile = item.assets["RGB"].href
    directory = Path(infile).parent / "tiles"
    subprocess.check_call(["gdal2tiles.py", "--xyz", infile, directory])
    item.assets["tiles"] = Asset(href=directory)
    return item
