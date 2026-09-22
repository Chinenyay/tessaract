from typing import TYPE_CHECKING, cast

from .provider import Provider

if TYPE_CHECKING:
    from anthropic import Anthropic


class AnthropicProvider(Provider):
    def __post__init__(self):
        try:
            from anthropic import Anthropic
        except ModuleNotFoundError as exc:
            if exc.name != "anthropic":
                raise
            raise ImportError(
                "Anthropic support requires the optional dependency"
                'Install it with: pip install "tessaract[anthropic]"'
            ) from exc
        
        self._client = Anthropic(api_key=self.api_key, **self.provider_args)

    def client(self) -> "Anthropic":
        return cast(Anthropic, self._client)