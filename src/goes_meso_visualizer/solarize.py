from pathlib import Path

import numpy
import pysolar.solar
import rasterio
import rioxarray
import scipy.interpolate
from pyproj import CRS, Transformer
from pystac import Asset, Item, MediaType


def item(item: Item) -> Item:
    source_crs = CRS(item.properties["proj:wkt2"])
    target_crs = CRS("EPSG:4326")
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    c01_path = Path(item.assets["C01_2km"].href)

    dataset = rioxarray.open_rasterio(c01_path)
    with rasterio.open(c01_path) as src:
        bounds = src.bounds
        meta = src.meta
    xs, ys = numpy.meshgrid(dataset.coords["x"].values, dataset.coords["y"].values)
    locations = transformer.transform(xs, ys)
    wgs84_bounds = transformer.transform_bounds(*bounds)
    sample_longitudes = numpy.linspace(wgs84_bounds[0], wgs84_bounds[2], 3)
    sample_latitudes = numpy.linspace(wgs84_bounds[1], wgs84_bounds[3], 3)

    points = list()
    solar_altitudes = list()
    for longitude in sample_longitudes:
        for latitude in sample_latitudes:
            points.append([longitude, latitude])
            solar_altitudes.append(
                pysolar.solar.get_altitude_fast(latitude, longitude, item.datetime)
            )
    raster = scipy.interpolate.griddata(
        numpy.array(points), numpy.array(solar_altitudes), locations
    )

    meta["count"] = 1
    meta["dtype"] = "float32"
    del meta["nodata"]
    stem = "_".join(c01_path.stem.split("_")[0:-1]) + "_SOLAR_ALTITUDE"
    path = c01_path.with_stem(stem)
    with rasterio.open(str(path), "w", **meta) as dst:
        dst.write(raster, 1)

    item.assets["solar_altitude"] = Asset(href=str(path), media_type=MediaType.COG)
    return item
