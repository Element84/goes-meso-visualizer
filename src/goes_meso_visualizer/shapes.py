import importlib.resources
import json

from geojson import FeatureCollection
from shapely.geometry import LineString, MultiLineString


def ep092023_best_track() -> MultiLineString:
    """Returns the best track of Hurricane Hilary"""
    return _read_track("ep092023_best_track.json")


def al132023_best_track() -> MultiLineString:
    """Returns the best track of Hurricane Lee."""
    return _read_track("al132023_best_track.json")


def _read_track(file_name: str) -> MultiLineString:
    line_strings = list()
    feature_collection = _read_track_feature_collection(file_name)
    for feature in feature_collection["features"]:
        line_strings.append(LineString(feature["geometry"]["coordinates"]))
    return MultiLineString(line_strings)


def _read_track_feature_collection(file_name: str) -> FeatureCollection:
    return FeatureCollection(
        json.loads(
            importlib.resources.files("goes_meso_visualizer.tracks")
            .joinpath(file_name)
            .read_text()
        )
    )
