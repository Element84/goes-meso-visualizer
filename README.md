# goes-meso-visualizer

Visualize GOES mesoscale data in a browser map.

## Running

```shell
pip install git+https://github.com/Element84/goes-meso-visualizer
```

The package comes with an example from the 2023 hurricane that struck the southwestern United States, Hilary:

```shell
goes-meso-visualizer build-example output
```

Use any old http server to serve the output directory:

```shell
http-server output
```

## Developing

```shell
git clone git@github.com:Element84/goes-meso-visualizer.git
cd goes-meso-visualizer
pip install -e '.[dev]'
pre-commit install
```

If you need a new requirement, add it to `requirements.in` (or `requirements-dev.in` for dev requirements), then:

```shell
scripts/update-requirements
```
