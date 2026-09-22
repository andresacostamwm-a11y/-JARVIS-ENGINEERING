import math
from .base import CalcResult,ENGINE_VERSION
G=9.80665;WATER_DENSITY_20C=998
def calculate_pump_power(flow_m3_h,head_m,efficiency=.75,density_kg_m3=WATER_DENSITY_20C):
 q=flow_m3_h/3600;ph=density_kg_m3*G*q*head_m;ps=ph/efficiency
 return CalcResult('hydraulic','pump_power','Pump Power',{'flow_m3_h':flow_m3_h,'head_m':head_m,'efficiency':efficiency},'P=ρgQH/η',{'p_shaft_kw':'kW'},['steady water flow'],{'q_m3_s':round(q,6),'p_hyd_kw':round(ph/1000,4),'p_shaft_kw':round(ps/1000,4)},'PASS' if efficiency>=.7 else 'WARN','efficiency check','Fluid mechanics',ENGINE_VERSION,__name__+'.calculate_pump_power')
def calculate_darcy_weisbach_head_loss(flow_m3_h,length_m,diameter_m,friction_factor=.02,density_kg_m3=998):
 area=math.pi*diameter_m**2/4;v=(flow_m3_h/3600)/area;hf=friction_factor*(length_m/diameter_m)*v**2/(2*G)
 return CalcResult('hydraulic','darcy_weisbach_head_loss','Darcy-Weisbach',{'flow_m3_h':flow_m3_h,'length_m':length_m,'diameter_m':diameter_m},'hf=f(L/D)v²/2g',{'hf_m':'m'},['minor losses excluded'],{'velocity_m_s':round(v,4),'hf_m':round(hf,4)},'PASS' if .5<=v<=3 else 'WARN','velocity check','Darcy-Weisbach',ENGINE_VERSION,__name__+'.calculate_darcy_weisbach_head_loss')
def calculate_flow_from_velocity(velocity_m_s,diameter_m):
 a=math.pi*diameter_m**2/4;q=velocity_m_s*a
 return CalcResult('hydraulic','flow_from_velocity','Flow from Velocity',{'velocity_m_s':velocity_m_s,'diameter_m':diameter_m},'Q=vA',{'q_m3_h':'m³/h'},['circular pipe'],{'q_m3_s':round(q,6),'q_m3_h':round(q*3600,4)},'PASS','continuity','Continuity equation',ENGINE_VERSION,__name__+'.calculate_flow_from_velocity')
