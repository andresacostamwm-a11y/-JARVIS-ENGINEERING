import math
from app.services.calculations.electrical import *
def test_voltage_drop_known_result():
 r=calculate_voltage_drop(100,80,35,480);expected=math.sqrt(3)*100*(COPPER_RESISTIVITY_75C/35)*80
 assert abs(r.result['vd_v']-expected)<.01 and r.check_status=='PASS'
def test_three_phase_power_known_result():
 r=calculate_three_phase_power(480,100,.9);assert abs(r.result['p_kw']-74.8246)<.01
def test_cable_ampacity():
 assert calculate_cable_ampacity_check(100,125).check_status=='PASS'
 assert calculate_cable_ampacity_check(100,100).check_status=='FAIL'
