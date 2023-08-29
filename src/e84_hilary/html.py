from pathlib import Path
from typing import cast

import pystac.utils
import rasterio
from jinja2 import Environment, PackageLoader
from pyproj import CRS, Transformer
from pystac import ItemCollection


def item_collection(item_collection: ItemCollection) -> str:
    environment = Environment(loader=PackageLoader("e84_hilary"))
    template = environment.get_template("index.html")
    sources = list()
    layers = list()
    for i, item in enumerate(item_collection):
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
