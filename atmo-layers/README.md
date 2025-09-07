# Atmospheric Layer Classifier (Python)

Classify an altitude into Earth's atmospheric layers and get:
- **Layer extent**
- **Temperature behavior**
- **Composition**
- **Notable phenomena**

## Highlights
- Clean **CLI** (single altitude or **batch CSV**)
- **JSON / JSONL / CSV** output for pipelines
- **FastAPI** app (`/layer`, `/batch`) for web demos
- Engineering polish: typing, dataclasses, self-checks, **pytest**, **ruff**, **mypy**, and **CI**

## Quickstart
```bash
# Single
python src/atmo_layers.py 100
python src/atmo_layers.py 250 --miles --json

# Batch
echo -e "altitude\n0\n15\n50\n85\n600\n" > sample.csv
python src/atmo_layers.py --batch sample.csv --out results.csv
python src/atmo_layers.py --batch sample.csv --out results.jsonl

# API (optional)
pip install "fastapi>=0.111" "uvicorn>=0.30"
python -m src.atmo_layers --serve
# GET http://localhost:8000/layer?altitude=100&unit=km
```

## CSV Formats
- Minimal: column **`altitude`** (km)
- Explicit units: columns **`altitude`**, **`unit`** (km/mi)

## Notes
Layer boundaries are **approximate** (vary by latitude, season, and solar activity) and are treated as gradual transitions. Classification uses **inclusive lower** / **exclusive upper** bounds per layer.

## Roadmap
- Plot layer bands and sample altitudes
- Add Docker example to README
- Lightweight web UI (React) powered by the API
