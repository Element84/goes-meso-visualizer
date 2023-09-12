from pathlib import Path

import numpy
import rasterio
import rioxarray
import xarray
from pystac import Asset, Item, MediaType

from .constants import SOLAR_ALTITUDE_KEY, VISUAL_KEY


def item(
    item: Item,
    y: float = 2.2,
    resolution: int = 2,
    min_solar_altitude: float = 0,
    max_solar_altitude: float = 10,
) -> Item:
    """Colorize a GOES mesoscale STAC item.

    Has some magic:

    - Builds a synthetic green band, cribbed from
      https://planetarycomputer.microsoft.com/dataset/goes-cmi#Example-Notebook
    - Blends in IR colorization for nighttime, dawn, and dusk

    Needs, as COGs:

    - C01
    - C02
    - C03
    - C13
    - solar_altitude (calculated from `solarize`)

    Args:
        item: The STAC item
        y: The scaling factor for the RGB imagery
        resolution: The nominal resolution, in kilometers, of the imagery to use
        min_solar_altitude: Below this altitude, always use IR (blend in between)
        max_solar_altitude: Above this altitude, always use RGB (blend in between)

    Returns:
        Item: The item with the input bands removed, and the RGB image
    """
    daytime_bands = [
        f"C01_{resolution}km",
        f"C02_{resolution}km",
        f"C03_{resolution}km",
    ]
    nightime_band = f"C13_{resolution}km"
    all_bands = daytime_bands + [nightime_band, SOLAR_ALTITUDE_KEY]
    for band in all_bands:
        if band not in item.assets:
            raise ValueError(f"missing required asset: {band}")

    common_names = [
        item.assets[band].extra_fields["eo:bands"][0]["common_name"]
        for band in daytime_bands
    ]
    dataset = xarray.concat(
        [rioxarray.open_rasterio(item.assets[band].href) for band in daytime_bands],
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

    window_ir = rioxarray.open_rasterio(item.assets[nightime_band].href)
    window_ir = 1 - window_ir / window_ir.max(dim=["band", "x", "y"])
    window_ir = numpy.clip(window_ir ** (1 / y), 0, 1)

    weights = rioxarray.open_rasterio(item.assets[SOLAR_ALTITUDE_KEY].href).values
    weights[weights < min_solar_altitude] = min_solar_altitude
    weights[weights > max_solar_altitude] = max_solar_altitude
    weights = weights / max_solar_altitude

    for i in range(len(rgb.values)):
        rgb.values[i] = rgb.values[i] * weights + window_ir.values[0] * (1 - weights)
    rgb = (rgb * 256).astype(numpy.uint8)

    c01_path = Path(item.assets[daytime_bands[0]].href)
    with rasterio.open(str(c01_path)) as src:
        meta = src.meta

    meta["count"] = 3
    meta["dtype"] = "uint8"
    meta["nodata"] = 0
    stem = "_".join(c01_path.stem.split("_")[0:-1]) + "_RGB"
    path = c01_path.with_stem(stem)
    with rasterio.open(str(path), "w", **meta) as dst:
        dst.write(rgb)

    item.assets[VISUAL_KEY] = Asset(
        href=str(path), title="Visual", media_type=MediaType.COG, roles=["visual"]
    )
    for band in all_bands:
        del item.assets[band]

    return item
