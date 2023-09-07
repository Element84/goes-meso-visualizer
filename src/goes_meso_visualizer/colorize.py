# Cribbed from https://planetarycomputer.microsoft.com/dataset/goes-cmi#Example-Notebook

from pathlib import Path

import numpy
import rasterio
import rioxarray
import xarray
from pystac import Asset, Item, MediaType


def item(item: Item, y: float = 2.2) -> Item:
    bands = ["C01_2km", "C02_2km", "C03_2km"]
    common_names = [
        item.assets[band].extra_fields["eo:bands"][0]["common_name"] for band in bands
    ]
    dataset = xarray.concat(
        [rioxarray.open_rasterio(item.assets[band].href) for band in bands],
        dim="band",
    ).assign_coords(band=common_names)
    green = (
        0.45 * dataset.sel(band="red")
        + 0.1 * dataset.sel(band="nir09")
        + 0.45 * dataset.sel(band="blue")
    ).assign_coords(band="green")
    rgb = xarray.concat([dataset, green], dim="band").sel(band=["red", "green", "blue"])
    rgb_max = rgb.max(dim=["band", "y", "x"])
    if rgb_max > 0:
        rgb = rgb / rgb.max(dim=["band", "y", "x"])
        rgb = numpy.clip(rgb ** (1 / y), 0, 1)

    window_ir = rioxarray.open_rasterio(item.assets["C13_2km"].href)
    window_ir = 1 - window_ir / window_ir.max(dim=["band", "x", "y"])
    window_ir = numpy.clip(window_ir ** (1 / 2.2), 0, 1)

    weights = rioxarray.open_rasterio(item.assets["solar_altitude"].href).values
    weights[weights < 0] = 0
    weights[weights > 10] = 10
    weights = weights / 10

    for i in range(len(rgb.values)):
        rgb.values[i] = rgb.values[i] * weights + window_ir.values[0] * (1 - weights)
    rgb = (rgb * 256).astype(numpy.uint8)

    c01_path = Path(item.assets[bands[0]].href)
    with rasterio.open(str(c01_path)) as src:
        meta = src.meta

    meta["count"] = 3
    meta["dtype"] = "uint8"
    meta["nodata"] = 0
    stem = "_".join(c01_path.stem.split("_")[0:-1]) + "_RGB"
    path = c01_path.with_stem(stem)
    with rasterio.open(str(path), "w", **meta) as dst:
        dst.write(rgb)

    item.assets["visual"] = Asset(
        href=str(path), title="RGB", media_type=MediaType.COG, roles=["visual"]
    )
    del item.assets["C01_2km"]
    del item.assets["C02_2km"]
    del item.assets["C03_2km"]
    del item.assets["C13_2km"]
    del item.assets["solar_altitude"]

    return item
