from .adapters.openai_adapter import OpenAIAdapter
from .tools.function import FunctionTool
from .providers import OpenAIProvider, Provider, AnthropicProvider
from .request import Input, Output
from .response import Response
from .request import Request
from .input_types import UserMessage, ToolCallResult, InputItemUnion, Message
from .output_types import AssistantMessage, OutputItemUnion
from typing import cast

class Tessaract:
    def __init__(self, providers: dict[str, OpenAIProvider | AnthropicProvider]):
        self.providers = providers
        self.adapters: dict[str, OpenAIAdapter ] = {} # value should be a union of OpenAIAdapter | AnthropicAdapter once implemented
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

    def _normalize_output(self, item: AssistantMessage) -> list[Output]:
        return [
            Output(content=output_item)
            for output_item in item.content
        ]


    def _normalize_input(self, item: str | UserMessage | ToolCallResult) -> Input | ToolCallResult:
        if isinstance(item, str):
            return Input(role="user", content=item)

        if isinstance(item, ToolCallResult):
            return item
        
        if isinstance(item, UserMessage):
            return Input(
                role="user",
                content=item.content
            )
        
        raise TypeError(f"Unsupported message type: {type(item).__name__}")

    def flatten(self, items):
        for item in items:
            if isinstance(item, list):
                yield from self.flatten(item)
            else:
                yield item

    def _build_request_model(self, model: str, input: list[str | UserMessage | AssistantMessage | ToolCallResult | list], tools:list[FunctionTool]) -> Request:
        all_items = self.flatten(input)

        normalized_list = []

        for item in all_items:
            if isinstance(item, AssistantMessage):
                normalized_list.extend(self._normalize_output(item))
            else:
                normalized_list.append(self._normalize_input(item))

        return Request(
            model=model,
            input=normalized_list,
            tools=tools
        )

    def send(self, model: str, input: list[str | UserMessage | AssistantMessage], tools: list[FunctionTool] | None = None) -> Response | None:
        model_prefix, model_name = self._normalize_model_name(model=model)

        if model_prefix not in self.providers:
            raise ValueError("provider prefix must match registered provider in tessaract object")

        _request_provider = self.providers[model_prefix]

        _tools = tools if tools is not None else []

        _tessaract_request = self._build_request_model(model=model_name, input=input, tools=_tools)

        _api_key = _request_provider.api_key

        if _api_key is None:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        
        if isinstance(_request_provider, OpenAIProvider):

            adapter = self.adapters[model_prefix]

            _response = adapter.generate_sync(request=_tessaract_request)
            return cast(Response, _response)

        return None
