from pydantic import BaseModel,EmailStr,Field,ConfigDict
class ORMModel(BaseModel):model_config=ConfigDict(from_attributes=True)
class LoginRequest(BaseModel):email:EmailStr;password:str
class RefreshRequest(BaseModel):refresh_token:str
class TokenResponse(BaseModel):access_token:str;refresh_token:str;token_type:str='bearer'
class ChatMessage(BaseModel):role:str;content:str
class ChatRequest(BaseModel):messages:list[ChatMessage];use_tools:bool=True;stream:bool=False
class AgentRunRequest(BaseModel):prompt:str;use_tools:bool=True
class RagSearchRequest(BaseModel):query:str;limit:int=5
class DrawingNodeIn(BaseModel):node_key:str;node_type:str;label:str;position_x:float=0;position_y:float=0;asset_id:str|None=None;data:dict=Field(default_factory=dict)
class DrawingEdgeIn(BaseModel):edge_key:str;source_key:str;target_key:str;label:str|None=None;edge_type:str='default';data:dict=Field(default_factory=dict)
class DrawingCreate(BaseModel):name:str;drawing_type:str='schematic';project_id:str|None=None;viewport:dict=Field(default_factory=dict);nodes:list[DrawingNodeIn]=Field(default_factory=list);edges:list[DrawingEdgeIn]=Field(default_factory=list)
class DrawingUpdate(BaseModel):name:str|None=None;viewport:dict|None=None;nodes:list[DrawingNodeIn]|None=None;edges:list[DrawingEdgeIn]|None=None
