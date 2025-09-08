[![CI](https://github.com/Codrich/atmo-layers/actions/workflows/ci.yml/badge.svg)](https://github.com/Codrich/atmo-layers/actions/workflows/ci.yml)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12-blue)

# Atmospheric Layer Classifier

A Python CLI + FastAPI service that classifies a spacecraft’s altitude into Earth’s atmospheric layers and returns:  
layer name, extent, temperature behavior, composition, and notable phenomena.

## Features
- 🔎 **CLI**: classify a single altitude or run a CSV batch.
- 🌐 **API (FastAPI)**: `/layer` and `/batch` endpoints.
- 🧪 **Tests + CI**: pytest, mypy, ruff on GitHub Actions.
- 🧰 **Typed**: mypy-friendly types, clean structure.
- 📦 **Ready to containerize**: Dockerfile included.

## Quickstart

### CLI
```bash
python src/atmo_layers.py 100
python src/atmo_layers.py --batch sample.csv --out results.csv
# Miles input
python src/atmo_layers.py 62 --miles

pip install fastapi uvicorn
python -m src.atmo_layers --serve
# then open: http://127.0.0.1:8000/docs

Atmospheric Layer Report @ 100.0 km (~100.0 km)
-----------------------------------------------
Layer: Thermosphere
Extent: ~85 to ~600 km (variable); blends upward toward the exosphere.
Temperature: Temperature increases dramatically with altitude (absorption of high-energy solar radiation).
Composition: Extremely thin; atomic O, N, He; significant ionization (overlaps with ionosphere).
Notable phenomena: Auroras (~100–300 km); many LEO satellites; ISS orbits ~400 km.
Note: Ranges are approximate; boundaries are gradual and vary with latitude/season/solar activity.

pytest -q
mypy src
ruff check .

Roadmap

Coverage + Codecov badge

Configurable layer boundaries

Plot temperature vs. altitude (matplotlib)

Publish package to PyPI

[![CI](https://github.com/Codrich/atmo-layers/actions/workflows/ci.yml/badge.svg)](https://github.com/Codrich/atmo-layers/actions/workflows/ci.yml)
