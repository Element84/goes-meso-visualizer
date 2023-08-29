import asyncio
from pathlib import Path
from typing import Optional

import click
import tqdm
from pystac import ItemCollection
from stac_asset import (  # We use the "private" _cli module to get progress reporting
    _cli,
)

import e84_hilary.colorize
import e84_hilary.goes  # TODO this should probably be search.goes
import e84_hilary.html
import e84_hilary.solarize
import e84_hilary.tile


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("OUTFILE")
@click.option("-m", "--max-items", type=int)
def search(outfile: str, max_items: Optional[int]) -> None:
    """Search for the required assets."""
    item_collection = e84_hilary.goes.search(max_items=max_items)
    item_collection.save_object(outfile)


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
def colorize(infile: str, outfile: str) -> None:
    """Colorizes an item collection"""
    item_collection = ItemCollection.from_file(infile)
    items = list()
    for item in tqdm.tqdm(item_collection):
        if "RGB" in item.assets:
            items.append(item)
        else:
            items.append(e84_hilary.colorize.item(item))
    ItemCollection(items).save_object(outfile)


@cli.command()
@click.argument("INFILE")
@click.argument("OUTFILE")
def solarize(infile: str, outfile: str) -> None:
    """Adds solar altitude tiff to an item collection"""
    item_collection = ItemCollection.from_file(infile)
    items = list()
    for item in tqdm.tqdm(item_collection):
        if "solar_altitude" in item.assets:
            items.append(item)
        else:
            items.append(e84_hilary.solarize.item(item))
    ItemCollection(items).save_object(outfile)


@cli.command()
@click.argument("INFILE")
@click.argument("OUTFILE")
def tile(infile: str, outfile: str) -> None:
    """Tiles an item collection"""
    item_collection = ItemCollection.from_file(infile)
    items = list()
    for item in tqdm.tqdm(item_collection):
        if "tiles" in item.assets:
            items.append(item)
        else:
            items.append(e84_hilary.tile.item(item))
    ItemCollection(items).save_object(outfile)


@cli.command()
@click.argument("INFILE")
@click.argument("OUTFILE")
def html(infile: str, outfile: str) -> None:
    """Builds an html page"""
    item_collection = ItemCollection.from_file(infile)
    html = e84_hilary.html.item_collection(item_collection)
    with open(outfile, "w") as f:
        f.write(html)
