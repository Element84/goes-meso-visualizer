import datetime
from typing import Optional

import shapely.geometry
import tqdm
from dateutil import rrule
from dateutil.rrule import HOURLY
from pystac import ItemCollection
from pystac_client import Client
from pystac_client.item_search import IntersectsLike


def goes(
    intersects: Optional[IntersectsLike],
    start: datetime.datetime,
    end: datetime.datetime,
    max_items: Optional[int] = None,
) -> ItemCollection:
    """Search the Planetary Computer's GOES collection for the assets we need.

    For now, hardcoded to hourly.

    We can't use intersects in the search itself because that breaks the
    Planetary Computer.

    Args:
        intersects: The geographic area to search
        start: The start datetime
        end: The end datetime
        max_items: The maximum number of items to find.

    Returns:
        ItemCollection: The items
    """
    planetary_computer = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1"
    )
    hours = list(rrule.rrule(HOURLY, dtstart=start, until=end))
    items = list()
    shape = shapely.geometry.shape(intersects)
    for dt in tqdm.tqdm(hours):
        search = planetary_computer.search(
            collections=["goes-cmi"],
            datetime=[dt, dt + datetime.timedelta(hours=1)],
            query={"goes:image-type": {"eq": "MESOSCALE"}},
            sortby="+datetime",
        )
        for item in search.items():
            if shape.intersects(shapely.geometry.shape(item.geometry)):
                items.append(item)
                break
        if max_items and len(items) >= max_items:
            break
    return ItemCollection(items)
