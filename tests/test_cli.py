import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from goes_meso_visualizer.cli import cli
from pystac import ItemCollection

ROOT = Path(__file__).parents[1]
TEST_DATA = ROOT / "tests" / "data"


@pytest.mark.vcr
def test_search() -> None:
    cli_runner = CliRunner(mix_stderr=False)
    result = cli_runner.invoke(
        cli,
        [
            "search",
            str(
                ROOT
                / "src"
                / "goes_meso_visualizer"
                / "tracks"
                / "ep092023_best_track.json"
            ),
            "--max-items",
            "1",
            "--start",
            "2023-08-17T03:00:29.400000Z",
        ],
    )
    assert result.exit_code == 0
    item_collection = ItemCollection.from_dict(json.loads(result.stdout.strip()))
    assert len(item_collection) == 1


@pytest.mark.slow
def test_download(tmp_path: Path) -> None:
    cli_runner = CliRunner(mix_stderr=False)
    result = cli_runner.invoke(
        cli,
        ["download", str(TEST_DATA / "search.json"), str(tmp_path / "download.json")],
    )
    assert result.exit_code == 0
    item_collection = ItemCollection.from_file(str(tmp_path / "download.json"))
    assert len(item_collection) == 1
    item = item_collection.items[0]
    assert len(item.assets) == 4
    assert "C01_2km" in item.assets
    assert "C02_2km" in item.assets
    assert "C03_2km" in item.assets
    assert "C13_2km" in item.assets


@pytest.mark.skip("We can't handle relative paths in the item collection yet")
def test_solarize(tmp_path: Path) -> None:
    cli_runner = CliRunner(mix_stderr=False)
    result = cli_runner.invoke(
        cli,
        [
            "download",
            str(TEST_DATA / "download.json"),
            str(tmp_path / "solarize.json"),
        ],
    )
    assert result.exit_code == 0
    item_collection = ItemCollection.from_file(str(tmp_path / "solarize.json"))
    assert len(item_collection) == 1
    item = item_collection.items[0]
    assert len(item.assets) == 5
    assert "C01_2km" in item.assets
    assert "C02_2km" in item.assets
    assert "C03_2km" in item.assets
    assert "C13_2km" in item.assets
    assert "solar_altitude" in item.assets
