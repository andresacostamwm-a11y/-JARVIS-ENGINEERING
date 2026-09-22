from abc import ABC,abstractmethod
class AIProvider(ABC):
 name='base'
 @abstractmethod
 def is_available(self):...
 @abstractmethod
 async def chat(self,messages,tools=None,temperature=.2):...
 @abstractmethod
 async def chat_stream(self,messages,tools=None,temperature=.2):...
def get_ai_provider():
 from app.services.ai.xai_provider import XAIProvider
 from app.core.config import get_settings
 s=get_settings();return XAIProvider(s.xai_api_key,s.xai_base_url,s.xai_model)
