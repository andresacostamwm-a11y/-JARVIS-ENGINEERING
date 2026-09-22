"""Hydraulic calc unit tests — known_input / known_result / tolerance."""
import math
from app.services.calculations.hydraulic import (
    calculate_pump_power,
    calculate_darcy_weisbach_head_loss,
    calculate_flow_from_velocity,
    G,
    WATER_DENSITY_20C,
)


def test_pump_power_known():
    # Q=450 m³/h, H=35 m, η=0.75
    r = calculate_pump_power(450, 35, 0.75, WATER_DENSITY_20C)
    q = 450 / 3600
    p_hyd = WATER_DENSITY_20C * G * q * 35
    p_shaft_kw = (p_hyd / 0.75) / 1000
    assert abs(r.result["p_shaft_kw"] - p_shaft_kw) < 0.01
    assert r.check_status == "PASS"
    assert r.discipline == "hydraulic"


def test_darcy_weisbach_known():
    r = calculate_darcy_weisbach_head_loss(100, 100, 0.2, 0.02)
    area = math.pi * (0.2**2) / 4
    v = (100 / 3600) / area
    hf = 0.02 * (100 / 0.2) * (v**2) / (2 * G)
    assert abs(r.result["hf_m"] - hf) < 0.001
    assert abs(r.result["velocity_m_s"] - v) < 0.001


def test_flow_from_velocity():
    r = calculate_flow_from_velocity(2.0, 0.1)
    area = math.pi * (0.1**2) / 4
    expected_m3_h = 2.0 * area * 3600
    assert abs(r.result["q_m3_h"] - expected_m3_h) < 0.01
