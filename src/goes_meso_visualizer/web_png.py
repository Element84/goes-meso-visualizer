from pathlib import Path

import rasterio
import rasterio.warp
from pystac import Asset, Item
from rasterio.warp import Resampling


def item(item: Item) -> Item:
    # https://rasterio.readthedocs.io/en/latest/topics/reproject.html
    asset = item.assets["visual"]
    dst_crs = "EPSG:3857"
    stem = "_".join(Path(asset.href).stem.split("_")[0:-1]) + "_RGB"
    path = Path(asset.href).with_stem(stem).with_suffix(".png")
    with rasterio.open(asset.href) as src:
        transform, width, height = rasterio.warp.calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )
        kwargs = src.meta.copy()
        kwargs.update(
            {
                "crs": dst_crs,
                "transform": transform,
                "width": width,
                "height": height,
                "driver": "PNG",
            }
        )
        with rasterio.open(path, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                rasterio.warp.reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.cubic,
                )
    item.assets["web_png"] = Asset(href=str(path), extra_fields={"proj:epsg": 3857})
    del item.assets["visual"]

    return item
