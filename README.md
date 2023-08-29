# 2023-08-Hilary

A demonstration of flood analysis after the August 2023 hurricane that struck California.

## Running

```shell
git clone https://github.com/Element84/2023-08-Hilary
cd 2023-08-Hilary
pip install .
```

Then download and build all of the assets:

```shell
e84-hilary download-and-build assets
```

To serve the website:

```shell
e84-hilary serve assets
```

## Developing

```shell
pip install -e '.[dev]'
pre-commit install
```

If you need a new requirement, add it to `requirements.in` (or `requirements-dev.in` for dev requirements), then:

```shell
scripts/update-requirements
```
