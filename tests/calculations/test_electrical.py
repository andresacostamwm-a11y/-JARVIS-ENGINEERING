"""Electrical calc unit tests — known_input / known_result / tolerance."""
import math
from app.services.calculations.electrical import (
    calculate_voltage_drop,
    calculate_three_phase_power,
    calculate_cable_ampacity_check,
    COPPER_RESISTIVITY_75C,
)


def test_voltage_drop_known_3phase():
    # Hand calc: R = 0.0214/35 Ω/m; Vd = √3 · I · R · L
    r = calculate_voltage_drop(
        current_a=100,
        length_m=80,
        conductor_area_mm2=35,
        voltage_v=480,
        phases=3,
        material="copper",
    )
    expected_r = COPPER_RESISTIVITY_75C / 35
    expected_vd = math.sqrt(3) * 100 * expected_r * 80
    expected_pct = expected_vd / 480 * 100
    assert abs(r.result["vd_v"] - expected_vd) < 0.01
    assert abs(r.result["vd_pct"] - expected_pct) < 0.01
    assert r.check_status == "PASS"
    assert r.inputs["current_a"] == 100
    assert r.formula
    assert r.units["vd_pct"] == "%"
    assert r.assumptions
    assert r.source
    assert r.version
    assert r.engine_module.endswith("calculate_voltage_drop")


def test_voltage_drop_fail_high():
    r = calculate_voltage_drop(
        current_a=200,
        length_m=500,
        conductor_area_mm2=10,
        voltage_v=230,
        phases=1,
    )
    assert r.result["vd_pct"] > 5
    assert r.check_status == "FAIL"


def test_three_phase_power_known():
    r = calculate_three_phase_power(480, 100, 0.9, 1.0)
    expected_kw = (math.sqrt(3) * 480 * 100 * 0.9) / 1000
    assert abs(r.result["p_kw"] - expected_kw) < 0.01
    assert r.check_status == "PASS"


def test_cable_ampacity_continuous():
    r = calculate_cable_ampacity_check(100, 125, continuous_load=True, safety_factor=1.25)
    assert r.result["required_a"] == 125.0
    assert r.result["adequate"] is True
    assert r.check_status == "PASS"

    r2 = calculate_cable_ampacity_check(100, 100, continuous_load=True)
    assert r2.check_status == "FAIL"
