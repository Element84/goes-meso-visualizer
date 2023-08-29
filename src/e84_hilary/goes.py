import datetime
from typing import Optional

import shapely.geometry
import tqdm
from dateutil import rrule
from dateutil.rrule import HOURLY
from pystac import ItemCollection
from pystac_client import Client

from . import shapes
from .constants import DISSIPATED, FORMED


def search(max_items: Optional[int] = None) -> ItemCollection:
    """Search the Planetary Computer's GOES collection for the assets we need."""
    planetary_computer = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1"
    )
    shape = shapes.ep092023_best_track()
    hours = list(rrule.rrule(HOURLY, dtstart=FORMED, until=DISSIPATED))
    items = list()
    for dt in tqdm.tqdm(hours):
        search = planetary_computer.search(
            collections=["goes-cmi"],
            datetime=[dt, dt + datetime.timedelta(hours=1)],
            query={"goes:image-type": {"eq": "MESOSCALE"}},
            max_items=10,
            sortby="+datetime",
        )
        for item in search.items():
            if shape.intersects(shapely.geometry.shape(item.geometry)):
                items.append(item)
                break
        if max_items and len(items) >= max_items:
            break
    return ItemCollection(items)
