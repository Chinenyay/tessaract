from ..providers import OpenAIProvider


class OpenAIAdapter:
    def __init__(self, provider: OpenAIProvider):
        self._provider = provider
        self._client = self._provider.client

    