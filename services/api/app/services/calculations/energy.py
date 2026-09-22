from .base import CalcResult,ENGINE_VERSION
AIR_CP=1.006;AIR_DENSITY=1.2
def calculate_cooling_load_basic(airflow_m3_h,delta_t_k,sensible_fraction=1):
 m=AIR_DENSITY*airflow_m3_h/3600;q=m*AIR_CP*delta_t_k*sensible_fraction
 return CalcResult('energy','cooling_load_basic','Basic Sensible Cooling Load',{'airflow_m3_h':airflow_m3_h,'delta_t_k':delta_t_k},'Q=ρ·Q̇·cp·ΔT',{'q_kw':'kW'},['sea-level air'],{'mass_flow_kg_s':round(m,4),'q_kw':round(q,4),'tons_tr':round(q/3.517,4)},'PASS','basic check','ASHRAE fundamentals',ENGINE_VERSION,__name__+'.calculate_cooling_load_basic')
def calculate_chiller_cop(cooling_capacity_kw,power_input_kw):
 cop=cooling_capacity_kw/power_input_kw;check='PASS' if cop>=4 else 'WARN' if cop>=2.5 else 'FAIL'
 return CalcResult('energy','chiller_cop','Chiller COP',{'cooling_capacity_kw':cooling_capacity_kw,'power_input_kw':power_input_kw},'COP=Q/W',{'cop':'-'},['steady state'],{'cop':round(cop,4),'eer':round(cop*3.412,4)},check,'COP check','AHRI / ASHRAE',ENGINE_VERSION,__name__+'.calculate_chiller_cop')
def calculate_energy_cost(power_kw,hours,tariff_per_kwh):
 e=power_kw*hours
 return CalcResult('energy','energy_cost','Energy Cost',{'power_kw':power_kw,'hours':hours,'tariff_per_kwh':tariff_per_kwh},'E=P·t; Cost=E·tariff',{'energy_kwh':'kWh'},['flat tariff'],{'energy_kwh':e,'cost':round(e*tariff_per_kwh,4)},'PASS','deterministic','Basic energy economics',ENGINE_VERSION,__name__+'.calculate_energy_cost')
