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

    def _normalize_input(self, item: Message) -> Input:
        if isinstance(item, UserMessage):
            return Input(
                role="user",
                content=item.content
            )
        raise TypeError(f"Unsupported message type: {type(item).__name__}")

    def _build_request_model(self, model: str, input: list[Message]) -> Request:
        normalized_input = [self._normalize_input(item) for item in input]
        return Request(
            model=model,
            input=normalized_input
        )

    def send(self, model: str, input: list[Message]) -> Response | None:
        model_prefix, model_name = self._normalize_model_name(model=model)

        if model_prefix not in self.providers:
            raise ValueError("provider prefix must match registered provider in tessaract object")

        _request_provider = self.providers[model_prefix]

        _tessaract_request = self._build_request_model(model=model_name, input=input)

        _api_key = _request_provider.api_key

        if _api_key is None:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        
        if isinstance(_request_provider, OpenAIProvider):

            _request = OpenAIAdapter(request=_tessaract_request, api_key=_api_key)
            _response = _request.generate_sync()
            return _response

        return None
