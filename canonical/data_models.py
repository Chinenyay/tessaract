from typing import Optional
from pydantic import BaseModel

class Provider(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: Optional[int] = None
    max_retries: Optional[int] = None
    default_headers: Optional[int] = None
    default_query: Optional[int] = None

class OpenAIProvider(Provider):
    pass

class AnthropicProvider(Provider):
    pass

