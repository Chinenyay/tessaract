from .adapters.openai_adapter import OpenAIAdapter
from .providers import OpenAIProvider, Provider, AnthropicProvider
from .request import Input
from .response import Response
from .request import Request
from .input_types import UserMessage, Message, AssistantMessage
from typing import cast

class Tessaract:
    def __init__(self, providers: dict[str, OpenAIProvider | AnthropicProvider]):
        self.providers = providers
        self.adapters: dict[str, OpenAIAdapter ] = {} # alue should be a union of OpenAIAdapter | AnthropicAdapter once implemented
        self.register_adapter()

    def register_adapter(self):
        for prefix, provider in self.providers.items():
            if isinstance(provider, OpenAIProvider):
                adapter = OpenAIAdapter(provider)
            else:
                raise NotImplementedError("not yet implemented")
            self.adapters[prefix] = adapter

    def _normalize_model_name(self, model: str):
        model_parts = model.split("/")
        model_prefix = model_parts[0]
        model_name = model_parts[1]

        return (model_prefix, model_name)

    def _normalize_input(self, item: str | UserMessage | AssistantMessage) -> Input:
        if isinstance(item, UserMessage):
            return Input(
                role="user",
                content=item.content
            )
        if isinstance(item, AssistantMessage):
            return Input(
                role="assistant",
                content=item.content
            )
        raise TypeError(f"Unsupported message type: {type(item).__name__}")

    def _normalize_input_list(self, items: list):
        converted_inputs = []
        for el in items:
            if isinstance(el, UserMessage):
                converted_input = Input(
                    role="user",
                    content=el.content
                )
                converted_inputs.append(converted_input)
            if isinstance(el, AssistantMessage):
                converted_input = Input(
                    role="assistant",
                    content=el.content
                )
                converted_inputs.append(converted_input)
        return converted_inputs

    def flatten(self, items):
        for item in items:
            if isinstance(item, list):
                yield from self.flatten(item)
            else:
                yield item

    def _build_request_model(self, model: str, input: list[str | UserMessage | AssistantMessage | list]) -> Request:
        for item in input:
            all_items = self.flatten(item)

        normalized_list = [self._normalize_input_list(item) for item in all_items]
            
                
        
        return Request(
            model=model,
            input=normalized_list
        )

    def send(self, model: str, input: list[str | UserMessage | AssistantMessage]) -> Response | None:
        model_prefix, model_name = self._normalize_model_name(model=model)

        if model_prefix not in self.providers:
            raise ValueError("provider prefix must match registered provider in tessaract object")

        _request_provider = self.providers[model_prefix]

        _tessaract_request = self._build_request_model(model=model_name, input=input)

        _api_key = _request_provider.api_key

        if _api_key is None:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        
        if isinstance(_request_provider, OpenAIProvider):

            adapter = self.adapters[model_prefix]

            _response = adapter.generate_sync(request=_tessaract_request)
            return cast(Response, _response)

        return None
