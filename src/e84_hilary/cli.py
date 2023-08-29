import asyncio
from pathlib import Path

import click
import tqdm
from pystac import ItemCollection
from stac_asset import (  # We use the "private" _cli module to get progress reporting
    _cli,
)

import e84_hilary.colorize
import e84_hilary.goes
import e84_hilary.solarize


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("DIRECTORY")
def search(directory: str) -> None:
    """Search for the required assets."""
    item_collection = e84_hilary.goes.search()
    item_collection.save_object(str(Path(directory) / "goes-cmi.json"))


@cli.command()
@click.argument("INFILE")
@click.argument("DIRECTORY")
def download(infile: str, directory: str) -> None:
    """Download all assets."""
    asyncio.run(
        _cli.download_async(
            href=infile,
            directory=directory,
            alternate_assets=[],
            include=["C01_2km", "C02_2km", "C03_2km", "C13_2km"],
            exclude=[],
            file_name="goes-cmi.json",
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
        items.append(e84_hilary.solarize.item(item))
    ItemCollection(items).save_object(outfile)
