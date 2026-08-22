from typing import cast
from dataclasses import dataclass, field

from openai import OpenAI

@dataclass
class Provider:
    api_key: str | None = None
    base_url: str | None = None
    timeout: int | None = None
    max_retries: int | None = None
    default_headers: str | None = None
    default_query: int | None = None
    _client: object | None = None
    provider_args: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        raise NotImplementedError("not yet implemented")
    
    @property
    def client(self):
        raise NotImplementedError("not yet implemented")

@dataclass
class OpenAIProvider(Provider):
    def __post_init__(self):
        self._client = OpenAI(api_key=self.api_key, **self.provider_args)

    @property
    def client(self) -> OpenAI:
        return cast(OpenAI, self._client)



class AnthropicProvider(Provider):
    pass

