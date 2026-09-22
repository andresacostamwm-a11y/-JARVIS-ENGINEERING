import math
from .base import CalcResult,ENGINE_VERSION
COPPER_RESISTIVITY_75C=.0214;ALUMINUM_RESISTIVITY_75C=.035
def calculate_voltage_drop(current_a,length_m,conductor_area_mm2,voltage_v,phases=3,material='copper',power_factor=.85):
 if min(current_a,length_m,conductor_area_mm2,voltage_v)<=0:raise ValueError('inputs must be > 0')
 rho=COPPER_RESISTIVITY_75C if material.lower()=='copper' else ALUMINUM_RESISTIVITY_75C;k=math.sqrt(3) if phases==3 else 2;vd=k*current_a*(rho/conductor_area_mm2)*length_m;pct=vd/voltage_v*100;check='PASS' if pct<=3 else 'WARN' if pct<=5 else 'FAIL'
 return CalcResult('electrical','voltage_drop','Voltage Drop',locals()|{},'Vd=k·I·(ρ/A)·L; Vd%=100·Vd/V',{'vd_v':'V','vd_pct':'%'},['75°C resistivity','reactance neglected'],{'vd_v':round(vd,4),'vd_pct':round(pct,4)},check,'≤3% typical guidance','IEC 60364 / NEC guidance',ENGINE_VERSION,__name__+'.calculate_voltage_drop')
def calculate_three_phase_power(voltage_ll_v,current_a,power_factor=.9,efficiency=1):
 p=math.sqrt(3)*voltage_ll_v*current_a*power_factor*efficiency/1000
 return CalcResult('electrical','three_phase_power','Three-Phase Power',{'voltage_ll_v':voltage_ll_v,'current_a':current_a,'power_factor':power_factor,'efficiency':efficiency},'P=√3·V·I·PF·η',{'p_kw':'kW'},['balanced 3φ'],{'p_kw':round(p,4)},'PASS' if power_factor>=.85 else 'WARN','PF check','IEEE basic AC equations',ENGINE_VERSION,__name__+'.calculate_three_phase_power')
def calculate_cable_ampacity_check(load_current_a,cable_ampacity_a,continuous_load=True,safety_factor=1.25):
 req=load_current_a*(safety_factor if continuous_load else 1);ok=cable_ampacity_a>=req
 return CalcResult('electrical','cable_ampacity_check','Cable Ampacity Check',{'load_current_a':load_current_a,'cable_ampacity_a':cable_ampacity_a},'I_required=I_load·SF',{'required_a':'A'},['NEC continuous load factor'],{'required_a':round(req,2),'adequate':ok},'PASS' if ok else 'FAIL','Ampacity check','NEC 210.19 / 215.2',ENGINE_VERSION,__name__+'.calculate_cable_ampacity_check')
