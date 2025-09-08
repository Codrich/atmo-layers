import math
from src.atmo_layers import classify_layer, describe_altitude

def name_at(km: float):
    L = classify_layer(km)
    return L.name if L else None

def test_boundaries_inclusive_lower_exclusive_upper():
    assert name_at(0.0) == "Troposphere"
    assert name_at(14.9999) == "Troposphere"
    assert name_at(15.0) == "Stratosphere"
    assert name_at(49.9999) == "Stratosphere"
    assert name_at(50.0) == "Mesosphere"
    assert name_at(84.9999) == "Mesosphere"
    assert name_at(85.0) == "Thermosphere"
    assert name_at(599.9999) == "Thermosphere"
    assert name_at(600.0) == "Exosphere"
    assert name_at(9999.0) == "Exosphere"

def test_out_of_range():
    assert name_at(-0.0001) is None
    assert name_at(20000.0) is None

def test_units_miles_conversion():
    r = describe_altitude(62.1371, unit="mi")  # ~100 km
    assert r["layer"] in {"Thermosphere", "Mesosphere"}  # around boundary

def test_describe_has_expected_keys():
    r = describe_altitude(100, unit="km")
    for k in ["layer", "extent", "temperature_profile", "composition", "phenomena"]:
        assert k in r
