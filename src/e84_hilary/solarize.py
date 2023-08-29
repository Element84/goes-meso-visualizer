from pathlib import Path

import numpy
import pysolar.solar
import rasterio
import rioxarray
import tqdm
import xarray
from pyproj import CRS, Transformer
from pystac import Asset, Item, MediaType


def item(item: Item) -> Item:
    source_crs = CRS(item.properties["proj:wkt2"])
    target_crs = CRS("EPSG:4326")
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    dataset = rioxarray.open_rasterio(item.assets["C01_2km"].href)
    xs, ys = numpy.meshgrid(dataset.coords["x"].values, dataset.coords["y"].values)
    values = transformer.transform(xs, ys)

    solar_altitude = xarray.zeros_like(dataset[0]).assign_coords(band="solar_altitude")
    width, height = values[0].shape
    for i in tqdm.tqdm(range(width)):
        for j in range(height):
            solar_altitude[i, j] = pysolar.solar.get_altitude_fast(
                values[1][i][j],
                values[0][i][j],
                item.datetime,
            )

    c01_path = Path(item.assets["C01_2km"].href)
    with rasterio.open(str(c01_path)) as src:
        meta = src.meta

    meta["count"] = 1
    meta["dtype"] = "float64"
    del meta["nodata"]
    stem = "_".join(c01_path.stem.split("_")[0:-1]) + "_SOLAR_ALTITUDE"
    path = c01_path.with_stem(stem)
    with rasterio.open(str(path), "w", **meta) as dst:
        dst.write(solar_altitude, 1)

    item.assets["solar_altitude"] = Asset(href=str(path), media_type=MediaType.COG)
    return item
