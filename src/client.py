from typing import cast

from .providers import OpenAIProvider
from .adapters.openai_adapter import OpenAIAdapter
from .types.input_types import InputType, UserMessage
from .types.response import Response
from .types.request import Request

class Tessaract:
    def __init__(self, providers: dict[str, OpenAIProvider]):
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

    def _build_request_model(
        self,
        model: str,
        provider: str,
        input: str | list[str | InputType]
        # reasoning: ReasoningOptions,
        # tools: list[FunctionTool],
    ) -> Request:

        all_items = []

        """
        all_items = self.flatten(input)

        normalized_list = []

        for item in all_items:
            if isinstance(item, AssistantMessage):
                normalized_list.extend(self._normalize_output(item))
            else:
                normalized_list.append(self._normalize_input(item))
        """
        
        if isinstance(input, str):
            converted_item = UserMessage(content=input)
            all_items.append(converted_item.raw(self.adapters[provider]))

        for message in input:
            if isinstance(message, InputType):
                all_items.append(message.raw(self.adapters[provider]))


        return Request(
            model=model,
            input=all_items,
            # reasoning=reasoning,
            # tools=tools,
        )



    def send(
            self, model: str, 
            input: str | list[str | InputType],
            # reasoning: ReasoningOptions | None = None,
            # tools: list[FunctionTool] | None = None
        ) -> Response | None:

        provider, model = self._normalize_model_name(model=model)

        if provider not in self.providers:
            raise ValueError("provider prefix must match registered provider in tessaract object")

        _request_provider = self.providers[provider]

        # _tools = tools if tools is not None else []

        _tessaract_request = self._build_request_model(model=model, input=input, provider=provider)

        _api_key = _request_provider.api_key

        if _api_key is None:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        
        if isinstance(_request_provider, OpenAIProvider):

            adapter = self.adapters[provider]

            _response = adapter.generate_sync(request=_tessaract_request)
            return cast(Response, _response)

        return None