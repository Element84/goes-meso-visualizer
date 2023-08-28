#!/usr/bin/env python

# Cribbed from https://planetarycomputer.microsoft.com/dataset/goes-cmi#Example-Notebook

from pathlib import Path

import click
import numpy
import rasterio
import rasterio.mask
import rasterio.warp
import rioxarray
import shapely.ops
import xarray
from pyproj import CRS, Transformer
from pystac import ItemCollection
from shapely.geometry import Polygon

γ = 2.2
transformer = Transformer.from_crs(CRS("EPSG:4326"), CRS("EPSG:3857"), always_xy=True)
bounds = shapely.ops.transform(
    transformer.transform,
    Polygon(
        [
            [-123.54169, 27.42800],
            [-106.98963, 27.42800],
            [-106.98963, 40.20096],
            [-123.54169, 40.20096],
        ]
    ),
)


@click.command()
@click.argument("INFILE")
@click.argument("OUTDIR")
def main(infile: str, outdir: str) -> None:
    Path(outdir).mkdir(exist_ok=True)
    items = ItemCollection.from_file(infile)
    sorted_items = sorted(items, key=lambda item: item.datetime)
    for i, item in enumerate(sorted_items):
        bands = ["C01_2km", "C02_2km", "C03_2km"]
        common_names = [
            item.assets[band].extra_fields["eo:bands"][0]["common_name"]
            for band in bands
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
        rgb = xarray.concat([dataset, green], dim="band").sel(
            band=["red", "green", "blue"]
        )
        rgb = rgb / rgb.max(dim=["band", "y", "x"])
        rgb = (numpy.clip(rgb ** (1 / γ), 0, 1) * 256).astype(numpy.uint8)

        path = Path(item.assets[bands[0]].href)
        dst_crs = "EPSG:3857"
        with rasterio.open(str(path)) as f:
            src_transform = f.transform
            src_crs = f.crs
            transform, width, height = rasterio.warp.calculate_default_transform(
                f.crs, dst_crs, f.width, f.height, *f.bounds
            )

        stem_base = "_".join(path.stem.split("_")[0:-1])
        tif_path = str(path.with_stem(stem_base + "_RGB"))
        with rasterio.open(
            tif_path,
            "w",
            width=width,
            height=height,
            count=3,
            crs="EPSG:3857",
            transform=transform,
            dtype="uint8",
            nodata=0,
            photometric="RGB",
        ) as f:
            for i in range(0, 3):
                rasterio.warp.reproject(
                    source=rgb[i],
                    destination=rasterio.band(f, i + 1),
                    src_transform=src_transform,
                    src_crs=src_crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                )

        with rasterio.open(tif_path) as f:
            png_image, png_transform = rasterio.mask.mask(f, [bounds], crop=True)
            png_meta = f.meta

        png_meta.update(
            {
                "driver": "PNG",
                "height": png_image.shape[1],
                "width": png_image.shape[2],
                "transform": png_transform,
            }
        )
        with rasterio.open(str(Path(outdir) / f"{i}.png"), "w", **png_meta) as f:
            f.write(png_image)


if __name__ == "__main__":
    main()
