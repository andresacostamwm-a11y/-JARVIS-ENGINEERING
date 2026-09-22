import json,httpx
from app.services.ai.provider import AIProvider
class XAIProvider(AIProvider):
 name='xai'
 def __init__(self,api_key,base_url,model):self.api_key=(api_key or '').strip();self.base_url=base_url.rstrip('/');self.model=model
 def is_available(self):return bool(self.api_key)
 async def chat(self,messages,tools=None,temperature=.2):
  if not self.is_available():return {'content':'JARVIS AI no está configurado: falta XAI_API_KEY. Cálculos y activos siguen disponibles.','tool_calls':[],'model':'none','degraded':True}
  payload={'model':self.model,'messages':messages,'temperature':temperature};payload.update({'tools':tools,'tool_choice':'auto'} if tools else {})
  async with httpx.AsyncClient(timeout=60) as c:r=await c.post(f'{self.base_url}/chat/completions',headers={'Authorization':f'Bearer {self.api_key}'},json=payload);r.raise_for_status();d=r.json()
  m=d['choices'][0]['message'];return {'content':m.get('content') or '','tool_calls':[{'id':x.get('id'),'name':x['function']['name'],'arguments':x['function'].get('arguments','{}')} for x in m.get('tool_calls') or []],'model':d.get('model',self.model),'degraded':False}
 async def chat_stream(self,messages,tools=None,temperature=.2):
  if not self.is_available():yield 'JARVIS AI no está configurado: falta XAI_API_KEY.';return
  payload={'model':self.model,'messages':messages,'temperature':temperature,'stream':True}
  async with httpx.AsyncClient(timeout=120) as c:
   async with c.stream('POST',f'{self.base_url}/chat/completions',headers={'Authorization':f'Bearer {self.api_key}'},json=payload) as r:
    async for line in r.aiter_lines():
     if line.startswith('data: ') and line[6:]!='[DONE]':
      try:
       x=json.loads(line[6:]);text=x['choices'][0]['delta'].get('content');yield text if text else ''
      except Exception:pass
