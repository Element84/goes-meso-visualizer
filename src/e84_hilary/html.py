from pathlib import Path
from typing import cast

import pystac.utils
import rasterio
from jinja2 import Environment, PackageLoader
from pyproj import CRS, Transformer
from pystac import ItemCollection

IDS_TO_EXCLUDE = [
    "OR_ABI-L2-M1-M6_G18_s20232280000292",
    "OR_ABI-L2-M1-M6_G18_s20232280100292",
    "OR_ABI-L2-M1-M6_G18_s20232280200292",
    "OR_ABI-L2-M1-M6_G18_s20232280300292",
    "OR_ABI-L2-M1-M6_G18_s20232280400292",
    "OR_ABI-L2-M1-M6_G18_s20232280500292",
    "OR_ABI-L2-M1-M6_G18_s20232280600292",
    "OR_ABI-L2-M1-M6_G18_s20232280702264",
    "OR_ABI-L2-M1-M6_G18_s20232280800293",
    "OR_ABI-L2-M1-M6_G18_s20232280900293",
    "OR_ABI-L2-M1-M6_G18_s20232281000293",
    "OR_ABI-L2-M1-M6_G18_s20232281100293",
    "OR_ABI-L2-M1-M6_G18_s20232281200293",
    "OR_ABI-L2-M1-M6_G18_s20232281300293",
    "OR_ABI-L2-M1-M6_G18_s20232281400293",
    "OR_ABI-L2-M2-M6_G18_s20232281500564",
    "OR_ABI-L2-M2-M6_G18_s20232281600564",
    "OR_ABI-L2-M2-M6_G18_s20232281700564",
    "OR_ABI-L2-M2-M6_G18_s20232281800564",
    "OR_ABI-L2-M2-M6_G18_s20232281900564",
    "OR_ABI-L2-M2-M6_G18_s20232282000564",
    "OR_ABI-L2-M2-M6_G18_s20232282100564",
    "OR_ABI-L2-M2-M6_G18_s20232282200565",
    "OR_ABI-L2-M2-M6_G18_s20232282300565",
    "OR_ABI-L2-M2-M6_G18_s20232290000565",
    "OR_ABI-L2-M2-M6_G18_s20232290100565",
    "OR_ABI-L2-M2-M6_G18_s20232290200565",
    "OR_ABI-L2-M1-M6_G18_s20232291800295",
]


def item_collection(item_collection: ItemCollection) -> str:
    environment = Environment(loader=PackageLoader("e84_hilary"))
    template = environment.get_template("index.html")
    sources = list()
    layers = list()
    items = [item for item in item_collection if item.id not in IDS_TO_EXCLUDE]
    for i, item in enumerate(sorted(items, key=lambda item: item.datetime)):
        with rasterio.open(item.assets["RGB"].href) as dataset:
            bounds = dataset.bounds
            crs = CRS(dataset.crs)
        transformer = Transformer.from_crs(crs, CRS("EPSG:4326"))
        bounds = transformer.transform_bounds(*bounds)
        bounds = [bounds[1], bounds[0], bounds[3], bounds[2]]
        href = item.assets["tiles"].href
        path = pystac.utils.make_relative_href(
            href, str(Path(href).parents[1]), start_is_dir=True
        )[
            2:
        ]  # remove ./
        # TODO customizable
        url = f"/{path}" + r"/{z}/{x}/{y}.png"
        sources.append(
            {
                "type": "raster",
                "tiles": [url],
                "minzoom": 4,
                "maxzoom": 5,
                "bounds": bounds,
            }
        )
        layers.append(
            {
                "id": f"layer-{i}",
                "type": "raster",
                "source": f"source-{i}",
            }
        )
    return cast(str, template.render(sources=sources, layers=layers))
