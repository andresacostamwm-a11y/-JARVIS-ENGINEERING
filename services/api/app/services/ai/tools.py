import json
from app.services.calculations.electrical import calculate_voltage_drop
from app.services.calculations.hydraulic import calculate_pump_power
from app.services.calculations.energy import calculate_chiller_cop
from app.services.rag.search import simple_rag_search
TOOL_DEFINITIONS=[{'type':'function','function':{'name':'voltage_drop','description':'Deterministic voltage drop','parameters':{'type':'object','properties':{'current_a':{'type':'number'},'length_m':{'type':'number'},'conductor_area_mm2':{'type':'number'},'voltage_v':{'type':'number'}},'required':['current_a','length_m','conductor_area_mm2','voltage_v']}}},{'type':'function','function':{'name':'pump_power','description':'Pump shaft power','parameters':{'type':'object','properties':{'flow_m3_h':{'type':'number'},'head_m':{'type':'number'}},'required':['flow_m3_h','head_m']}}},{'type':'function','function':{'name':'chiller_cop','description':'Chiller COP','parameters':{'type':'object','properties':{'cooling_capacity_kw':{'type':'number'},'power_input_kw':{'type':'number'}},'required':['cooling_capacity_kw','power_input_kw']}}}]
def execute_tool(name,args,db):
 if isinstance(args,str):args=json.loads(args or '{}')
 if name=='voltage_drop':return calculate_voltage_drop(**args).to_dict()
 if name=='pump_power':return calculate_pump_power(**args).to_dict()
 if name=='chiller_cop':return calculate_chiller_cop(**args).to_dict()
 if name=='rag_search':return {'hits':simple_rag_search(db,args.get('query',''),args.get('limit',5))}
 return {'error':f'Unknown tool: {name}'}
