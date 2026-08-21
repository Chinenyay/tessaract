from .adapters.openai_adapter import OpenAIAdapter
from .providers import OpenAIProvider
from .request import Input
from .responses import Response
from .request import Request
from .input_types import UserMessage, Message


class Tessaract:
    def __init__(self, providers: dict[str, OpenAIProvider]):
        self.providers = providers

    def _normalize_model_name(self, model: str):
        model_parts = model.split("/")
        model_prefix = model_parts[0]
        model_name = model_parts[1]

        return (model_prefix, model_name)

    def _normalize_input(self, item: Message):
        if isinstance(item, UserMessage):
            return Input(
                role="user",
                content=item.content
            )

    def send(self, model: str, input: list[Message]) -> Response | None:
        model_prefix, model_name = self._normalize_model_name(model=model)

        if model_prefix not in self.providers:
            raise ValueError("provider prefix must match registered provider in tessaract object")
        
        normalized_input = [lambda item: self._normalize_input(item), input]

        _request_provider = self.providers[model_prefix]

        if isinstance(_request_provider, OpenAIProvider):

            _request = OpenAIAdapter()
            _response = _request.generate_sync(
                model=model_name,
                input=normalized_input
            )
            return _response

        return None
