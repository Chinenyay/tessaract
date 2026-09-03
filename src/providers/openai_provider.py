from typing import cast

from openai import OpenAI

from .provider import Provider


class OpenAIProvider(Provider):
    def __post_init__(self):
        self._client = OpenAI(api_key=self.api_key, **self.provider_args)

    @property
    def client(self) -> OpenAI:
        return cast(OpenAI, self._client)
