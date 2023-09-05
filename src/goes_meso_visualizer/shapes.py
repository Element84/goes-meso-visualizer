import importlib.resources
import json

from geojson import FeatureCollection
from shapely.geometry import LineString, MultiLineString


def ep092023_best_track() -> MultiLineString:
    line_strings = list()
    feature_collection = read_feature_collection("ep092023_best_track.json")
    for feature in feature_collection["features"]:
        line_strings.append(LineString(feature["geometry"]["coordinates"]))
    return MultiLineString(line_strings)


def read_feature_collection(file_name: str) -> FeatureCollection:
    return FeatureCollection(
        json.loads(
            importlib.resources.files("goes_meso_visualizer")
            .joinpath(file_name)
            .read_text()
        )
    )
