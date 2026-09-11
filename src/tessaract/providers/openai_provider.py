from typing import TYPE_CHECKING, cast

from .provider import Provider

if TYPE_CHECKING:
    from openai import OpenAI


class OpenAIProvider(Provider):
    def __post_init__(self) -> None:
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:
            if exc.name != "openai":
                raise
            raise ImportError(
                "OpenAI support requires the optional dependency"
                'Install it with: pip install "tessaract[openai]"'
            ) from exc

        self._client = OpenAI(api_key=self.api_key, **self.provider_args)

    @property
    def client(self) -> "OpenAI":
        return cast("OpenAI", self._client)
