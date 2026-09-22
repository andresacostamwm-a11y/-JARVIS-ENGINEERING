import math
from app.services.calculations.hydraulic import *
def test_pump_power_known_result():
 r=calculate_pump_power(450,35,.75);assert abs(r.result['p_shaft_kw']-57.091)<.01
def test_darcy_known_result():
 r=calculate_darcy_weisbach_head_loss(100,100,.2,.02);assert abs(r.result['hf_m']-.3986)<.001
def test_flow_from_velocity():
 r=calculate_flow_from_velocity(2,.1);assert abs(r.result['q_m3_h']-56.5487)<.01
