"""Energy calc unit tests — known_input / known_result / tolerance."""
from app.services.calculations.energy import (
    calculate_cooling_load_basic,
    calculate_chiller_cop,
    calculate_energy_cost,
    AIR_CP,
    AIR_DENSITY,
)


def test_cooling_load_known():
    r = calculate_cooling_load_basic(25000, 8.0)
    m = AIR_DENSITY * (25000 / 3600)
    q = m * AIR_CP * 8.0
    assert abs(r.result["q_kw"] - q) < 0.05
    assert r.check_status == "PASS"


def test_chiller_cop_known():
    r = calculate_chiller_cop(1758.5, 320)
    assert abs(r.result["cop"] - (1758.5 / 320)) < 0.001
    assert r.check_status == "PASS"


def test_energy_cost():
    r = calculate_energy_cost(100, 24, 0.12)
    assert r.result["energy_kwh"] == 2400.0
    assert abs(r.result["cost"] - 288.0) < 0.001
