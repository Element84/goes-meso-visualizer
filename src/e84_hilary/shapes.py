import importlib.resources
import json

import shapely.geometry
from shapely.geometry import MultiPolygon


def la_county() -> MultiPolygon:
    multi_polygon = shapely.geometry.shape(
        json.loads(
            importlib.resources.files("e84_hilary")
            .joinpath("la-county.json")
            .read_text()
        )["features"][3]["geometry"]
    )
    assert multi_polygon.geom_type == "MultiPolygon", multi_polygon.geom_type
    return multi_polygon
