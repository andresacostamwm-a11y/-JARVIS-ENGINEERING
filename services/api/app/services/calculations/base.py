from dataclasses import dataclass,asdict
from typing import Any
ENGINE_VERSION='1.0.0'
@dataclass
class CalcResult:
 discipline:str;calc_type:str;name:str;inputs:dict[str,Any];formula:str;units:dict[str,str];assumptions:list[str];result:dict[str,Any];check_status:str;check_notes:str;source:str;version:str=ENGINE_VERSION;engine_module:str=''
 def to_dict(self):return asdict(self)
