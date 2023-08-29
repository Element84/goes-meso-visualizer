import importlib.resources
import json

import shapely.geometry
from geojson import FeatureCollection
from shapely.geometry import LineString, MultiLineString, MultiPolygon


def la_county() -> MultiPolygon:
    multi_polygon = shapely.geometry.shape(
        read_feature_collection("la-country.json")["features"][3]["geometry"]
    )
    assert multi_polygon.geom_type == "MultiPolygon", multi_polygon.geom_type
    return multi_polygon


def ep092023_best_track() -> MultiLineString:
    line_strings = list()
    feature_collection = read_feature_collection("ep092023_best_track.json")
    for feature in feature_collection["features"]:
        line_strings.append(LineString(feature["geometry"]["coordinates"]))
    return MultiLineString(line_strings)


def read_feature_collection(file_name: str) -> FeatureCollection:
    return FeatureCollection(
        json.loads(
            importlib.resources.files("e84_hilary").joinpath(file_name).read_text()
        )
    )
