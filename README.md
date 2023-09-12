# goes-meso-visualizer

![Hilary](./img/hilary.gif)

Visualize GOES mesoscale data in a browser map.
Live demos are available:

- [Hurricane Hilary](https://demos.dev.element84.com/goes-meso-visualizer/hilary/)
- [Hurricane Lee](https://demos.dev.element84.com/goes-meso-visualizer/lee/)

## Running

```shell
git clone git@github.com:Element84/goes-meso-visualizer.git
cd goes-meso-visualizer
pip install .
```

This installs the `goes-meso-visualizer` command-line executable (CLI), which contains all the commands to build visualizations.
Run `goes-meso-visualizer --help` to see what's available.
We provide an example Makefile to build visualization from two 2023 hurricanes:

```shell
make site
npm install -g http-server  # if you don't have a preferred http server
http-server site
```

Then, navigate to <http://localhost:8080/hilary> or <http://localhost:8080/lee>.

## Developing

```shell
pip install -e '.[dev]'
pre-commit install
```

If you need a new requirement, add it to `requirements.in` (or `requirements-dev.in` for dev requirements), then:

```shell
scripts/update-requirements
```
