import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from goes_meso_visualizer.cli import cli
from pystac import ItemCollection


@pytest.mark.vcr
def test_search() -> None:
    cli_runner = CliRunner(mix_stderr=False)
    result = cli_runner.invoke(
        cli,
        [
            "search",
            str(
                Path(__file__).parents[1]
                / "src"
                / "goes_meso_visualizer"
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
