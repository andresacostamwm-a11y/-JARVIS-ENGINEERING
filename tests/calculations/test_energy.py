from app.services.calculations.energy import *
def test_cooling_load_known_result():
 r=calculate_cooling_load_basic(25000,8);assert abs(r.result['q_kw']-67.0667)<.05
def test_chiller_cop_known_result():
 r=calculate_chiller_cop(1758.5,320);assert abs(r.result['cop']-5.4953)<.001
def test_energy_cost():assert calculate_energy_cost(100,24,.12).result['cost']==288
