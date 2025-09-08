#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Iterable, Tuple
import argparse
import csv
import json
import os
import sys

KM_PER_MILE = 1.609344

@dataclass(frozen=True)
class Layer:
    name: str
    min_km: float            # inclusive lower bound (km)
    max_km: Optional[float]  # exclusive upper bound; None = open-ended
    extent_note: str
    temperature_profile: str
    composition: str
    phenomena: str

    def contains(self, altitude_km: float) -> bool:
        lower_ok = altitude_km >= self.min_km
        upper_ok = True if self.max_km is None else altitude_km < self.max_km
        return lower_ok and upper_ok

# Canonical layer set (approximate; boundaries vary with latitude/season/solar activity)
LAYERS: List[Layer] = [
    Layer(
        name="Troposphere",
        min_km=0.0,
        max_km=15.0,
        extent_note="Surface to ~10–15 km (lower at poles, higher at equator); top is the tropopause.",
        temperature_profile="Temperature generally decreases with altitude (~6.5 °C per km).",
        composition="Mostly N₂ and O₂ with water vapor and aerosols; highest gas density.",
        phenomena="All weather (clouds, rain, storms); strong vertical mixing."
    ),
    Layer(
        name="Stratosphere",
        min_km=15.0,
        max_km=50.0,
        extent_note="~15 to ~50 km; top is the stratopause.",
        temperature_profile="Temperature increases with altitude (ozone absorbs UV).",
        composition="Drier air; ozone (O₃) concentrated ~20–30 km; relatively stratified.",
        phenomena="Commercial jets and some high-altitude aircraft; ozone UV shielding; polar stratospheric clouds."
    ),
    Layer(
        name="Mesosphere",
        min_km=50.0,
        max_km=85.0,
        extent_note="~50 to ~85 km; top is the mesopause (coldest atmospheric region).",
        temperature_profile="Temperature decreases with altitude; coldest layer overall.",
        composition="Very thin air; mostly N₂ and O₂ with traces (e.g., CO₂, Na layer).",
        phenomena="Meteors ablate (‘shooting stars’); noctilucent clouds near the mesopause."
    ),
    Layer(
        name="Thermosphere",
        min_km=85.0,
        max_km=600.0,
        extent_note="~85 to ~600 km (variable); blends upward toward the exosphere.",
        temperature_profile="Temperature increases dramatically with altitude (absorption of high-energy solar radiation).",
        composition="Extremely thin; atomic O, N, He; significant ionization (overlaps with ionosphere).",
        phenomena="Auroras (~100–300 km); many LEO satellites; ISS orbits ~400 km."
    ),
    Layer(
        name="Exosphere",
        min_km=600.0,
        max_km=10000.0,
        extent_note="~600 km upward, gradually merging into space; no sharp upper boundary.",
        temperature_profile="No meaningful bulk temperature; particle energies high but densities extremely low.",
        composition="Extremely sparse H and He dominate; occasional heavier atoms.",
        phenomena="Very high orbits; spacecraft transition to space environment; ballistic particle trajectories."
    ),
]

def miles_to_km(miles: float) -> float:
    return miles * KM_PER_MILE

def classify_layer(altitude_km: float) -> Optional[Layer]:
    if altitude_km < 0:
        return None
    for layer in LAYERS:
        if layer.contains(altitude_km):
            return layer
    return None  # above our exosphere cap

def describe_altitude(altitude: float, unit: str = "km") -> Dict[str, Any]:
    if unit not in {"km", "mi"}:
        raise ValueError("unit must be 'km' or 'mi'")
    altitude_km = float(altitude if unit == "km" else miles_to_km(altitude))
    layer = classify_layer(altitude_km)

    result: Dict[str, Any] = {
        "input": {"altitude": altitude, "unit": unit, "altitude_km": round(altitude_km, 6)}
    }
    if layer is None:
        result["layer"] = None
        result["note"] = "Altitude is outside modeled ranges (below 0 km or above ~10,000 km)."
        return result

    result.update({
        "layer": layer.name,
        "extent": layer.extent_note,
        "temperature_profile": layer.temperature_profile,
        "composition": layer.composition,
        "phenomena": layer.phenomena,
        "references_note": "Ranges are approximate; boundaries are gradual and vary with latitude/season/solar activity."
    })
    return result

# ---------- Batch utilities ----------


def read_batch_csv(path: str) -> Iterable[Tuple[float, str]]:
    """
    Yields (altitude, unit) from a CSV file.
    Accepts either:
      - column 'altitude' [km]
      - columns 'altitude', 'unit' with unit in {'km','mi'}
    """
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if "altitude" not in r.fieldnames:
            raise ValueError("CSV must contain a column named 'altitude'.")
        unit_field = "unit" if "unit" in r.fieldnames else None
        for i, row in enumerate(r, start=2):
            if row.get("altitude") in (None, ""):
                raise ValueError(f"Row {i}: empty altitude")
            try:
                alt = float(row["altitude"])
            except ValueError:
                raise ValueError(f"Row {i}: altitude must be a number, got {row['altitude']!r}")
            unit = row[unit_field].strip().lower() if unit_field else "km"
            if unit not in {"km", "mi"}:
                raise ValueError(f"Row {i}: unit must be 'km' or 'mi', got {unit!r}")
            yield alt, unit

def write_results(path: str, reports: List[Dict[str, Any]]) -> None:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".json", ".jsonl"}:
        with open(path, "w", encoding="utf-8") as f:
            if ext == ".jsonl":
                for rec in reports:
                    f.write(json.dumps(rec) + "\n")
            else:
                json.dump(reports, f, indent=2)
    elif ext == ".csv":
        fields = [
            "input.altitude", "input.unit", "input.altitude_km",
            "layer", "extent", "temperature_profile", "composition", "phenomena", "note"
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(fields)
            for r in reports:
                def g(key: str):
                    if key.startswith("input."):
                        return r.get("input", {}).get(key.split(".", 1)[1], "")
                    return r.get(key, "")
                w.writerow([g(k) for k in fields])
    else:
        raise ValueError("Output file must end with .csv, .json, or .jsonl")

def _print_human(report: Dict[str, Any]) -> None:
    inp = report["input"]
    header = f"Atmospheric Layer Report @ {inp['altitude']} {inp['unit']} (~{inp['altitude_km']} km)"
    print(header)
    print("-" * len(header))
    if report.get("layer") is None:
        print(report.get("note", "No layer"))
        return
    print(f"Layer: {report['layer']}")
    print(f"Extent: {report['extent']}")
    print(f"Temperature: {report['temperature_profile']}")
    print(f"Composition: {report['composition']}")
    print(f"Notable phenomena: {report['phenomena']}")
    print(f"Note: {report['references_note']}")

def _self_checks() -> None:
    def layer_at(km: float) -> str:
        L = classify_layer(km)
        return L.name if L else "None"
    cases = {
        0.0: "Troposphere",
        14.9999: "Troposphere",
        15.0: "Stratosphere",
        50.0: "Mesosphere",
        84.9999: "Mesosphere",
        85.0: "Thermosphere",
        400.0: "Thermosphere",
        600.0: "Exosphere",
        9999.0: "Exosphere",
        -1.0: "None",
        20000.0: "None",
    }
    fails = [(km, exp, layer_at(km)) for km, exp in cases.items() if layer_at(km) != exp]
    if fails:
        raise AssertionError(f"Self-checks failed: {fails}")

# ---------- FastAPI (optional) ----------

def create_app():
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
    except Exception as e:
        raise RuntimeError("FastAPI is not installed. Run `pip install fastapi uvicorn`.") from e

    app = FastAPI(title="Atmospheric Layer Classifier", version="1.0.0")

    class Query(BaseModel):
        altitude: float
        unit: str = "km"

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/layer")
    def get_layer(altitude: float, unit: str = "km"):
        try:
            return describe_altitude(altitude, unit=unit)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/batch")
    def post_batch(items: List[Query]):
        out = []
        for q in items:
            out.append(describe_altitude(q.altitude, unit=q.unit))
        return out

    return app

def _serve(host: str = "0.0.0.0", port: int = 8000) -> None:
    try:
        import uvicorn  # type: ignore
    except Exception as e:
        raise RuntimeError("uvicorn is not installed. Run `pip install uvicorn`.") from e
    app = create_app()
    uvicorn.run(app, host=host, port=port)

# ---------- CLI ----------

def main() -> None:
    p = argparse.ArgumentParser(description="Classify altitude into an atmospheric layer and describe it.")
    g = p.add_mutually_exclusive_group(required=False)
    g.add_argument("altitude", nargs="?", type=float, help="Altitude value (km by default unless --miles)")
    g.add_argument("--batch", metavar="FILE", help="CSV with altitudes (and optional unit column)")

    p.add_argument("--miles", action="store_true", help="Interpret single altitude as miles (default: km)")
    p.add_argument("--json", action="store_true", help="Output JSON for single altitude")
    p.add_argument("--out", metavar="FILE", help="Write batch results to .csv / .json / .jsonl")
    p.add_argument("--no-checks", action="store_true", help="Skip self-checks")
    p.add_argument("--serve", action="store_true", help="Run FastAPI server (requires fastapi & uvicorn)")

    args = p.parse_args()

    if args.serve:
        _serve()
        return

    if not args.no_checks:
        _self_checks()

    if args.batch:
        try:
            rows = list(read_batch_csv(args.batch))
            reports = [describe_altitude(a, unit=u) for a, u in rows]
            if args.out:
                write_results(args.out, reports)
            else:
                for r in reports:
                    _print_human(r)
        except Exception as e:
            print(f"Batch error: {e}", file=sys.stderr)
            sys.exit(2)
        return

    if args.altitude is None:
        p.print_help()
        sys.exit(1)

    unit = "mi" if args.miles else "km"
    try:
        report = describe_altitude(args.altitude, unit=unit)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(report)

if __name__ == "__main__":
    main()
