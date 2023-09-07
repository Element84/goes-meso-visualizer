import asyncio
import datetime
import json
import shutil
from pathlib import Path
from typing import Optional

import click
import dateutil.parser
import geojson
import pystac.utils
import tqdm
from pystac import ItemCollection
from shapely.geometry import LineString, MultiLineString
from stac_asset import (  # We use the "private" _cli module to get progress reporting
    _cli,
)

import goes_meso_visualizer.colorize
import goes_meso_visualizer.search
import goes_meso_visualizer.solarize
import goes_meso_visualizer.web_png


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("INFILE")
@click.option("-s", "--start")
@click.option("-e", "--end")
@click.option("-m", "--max-items", type=int)
def search(
    infile: str,
    start: Optional[str],
    end: Optional[str],
    max_items: Optional[int],
) -> None:
    """Search for the required assets."""
    with open(infile) as f:
        intersects = geojson.load(f)
    if intersects["type"] == "FeatureCollection":
        if intersects["features"][0]["geometry"]["type"] == "LineString":
            intersects = MultiLineString(
                [
                    LineString(
                        line_string["geometry"]["coordinates"][0]
                        for line_string in intersects["features"]
                    )
                ]
            )
        else:
            raise NotImplementedError

    now = datetime.datetime.now()
    if start:
        start_datetime = dateutil.parser.parse(start)
    elif end:
        raise ValueError("cannot specify end without a start")
    else:
        start_datetime = now - datetime.timedelta(days=1)
    if end:
        end_datetime = dateutil.parser.parse(end)
    elif start is not None:
        end_datetime = start_datetime + datetime.timedelta(days=1)
    else:
        end_datetime = now
    item_collection = goes_meso_visualizer.search.goes(
        intersects=intersects,
        start=start_datetime,
        end=end_datetime,
        max_items=max_items,
    )
    print(json.dumps(item_collection.to_dict(transform_hrefs=False)))


@cli.command()
@click.argument("INFILE")
@click.argument("OUTFILE")
def download(infile: str, outfile: str) -> None:
    """Download all assets."""
    directory = Path(outfile).parent
    file_name = Path(outfile).name
    asyncio.run(
        _cli.download_async(
            href=infile,
            directory=str(directory),
            alternate_assets=[],
            include=["C01_2km", "C02_2km", "C03_2km", "C13_2km"],
            exclude=[],
            file_name=file_name,
            quiet=False,
            s3_requester_pays=False,
            s3_retry_mode="adaptive",
            s3_max_attempts=10,
            keep=False,
            fail_fast=False,
            overwrite=False,
        )
    )


@cli.command()
@click.argument("INFILE")
@click.argument("OUTFILE")
def solarize(infile: str, outfile: str) -> None:
    """Adds solar altitude tiff to an item collection"""
    item_collection = ItemCollection.from_file(infile)
    items = list()
    for item in tqdm.tqdm(item_collection):
        items.append(goes_meso_visualizer.solarize.item(item))
    ItemCollection(items).save_object(outfile)


@cli.command()
@click.argument("INFILE")
@click.argument("OUTFILE")
def colorize(infile: str, outfile: str) -> None:
    """Colorizes an item collection"""
    item_collection = ItemCollection.from_file(infile)
    items = list()
    for item in tqdm.tqdm(item_collection):
        items.append(goes_meso_visualizer.colorize.item(item))
    ItemCollection(items).save_object(outfile)


@cli.command()
@click.argument("INFILE")
@click.argument("OUTFILE")
def web_png(infile: str, outfile: str) -> None:
    """Creates a PNG version of the colorized images for web viz"""
    item_collection = ItemCollection.from_file(infile)
    items = list()
    for item in tqdm.tqdm(item_collection):
        items.append(goes_meso_visualizer.web_png.item(item))
    ItemCollection(items).save_object(outfile)


@cli.command()
@click.argument("ITEM_COLLECTION")
@click.argument("HTML")
@click.argument("OUTDIR")
def build(item_collection: str, html: str, outdir: str) -> None:
    outdir_path = Path(outdir).absolute()
    if outdir_path.exists():
        shutil.rmtree(outdir_path)
    outdir_path.mkdir(parents=True)
    with open(item_collection) as f:
        data = json.load(f)
    for item in data["features"]:
        for asset in item["assets"].values():
            relative_href = pystac.utils.make_relative_href(
                asset["href"],
                Path(item_collection).parent.absolute(),
                start_is_dir=True,
            )
            path = outdir_path / relative_href
            path.parent.mkdir(exist_ok=True)
            shutil.copyfile(asset["href"], path)
            asset["href"] = relative_href
    with open(outdir_path / "item-collection.json", "w") as f:
        json.dump(data, f)
    shutil.copyfile(html, Path(outdir) / "index.html")


if __name__ == "__main__":
    cli()
