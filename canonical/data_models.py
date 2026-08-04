from pydantic import BaseModel

class Provider(BaseModel):
    api_key: str | None = None
    base_url: str | None = None
    timeout: int | None = None
    max_retries: int | None = None
    default_headers: str | None = None
    default_query: int | None = None

class OpenAIProvider(Provider):
    pass

class AnthropicProvider(Provider):
    pass

