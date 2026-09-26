import os
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
                "OpenAI support requires the optional dependency. "
                'Install it with: pip install "tessaract[openai]"'
            ) from exc

        if self.api_key is None:
            self.api_key = os.environ.get("OPENAI_API_KEY")

        if self.api_key is None:
            raise ValueError(
                "No OpenAI API key found. Pass api_key to OpenAIProvider "
                "or set the OPENAI_API_KEY environment variable."
            )

        self._client = OpenAI(**self._client_kwargs())

    @property
    def client(self) -> "OpenAI":
        return cast("OpenAI", self._client)
