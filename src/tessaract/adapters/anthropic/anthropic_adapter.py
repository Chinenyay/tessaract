import json
from collections.abc import Iterator, Sequence
from typing import cast


from ...providers.anthropic_provider import AnthropicProvider

from ...tools.function import InputSchema
from ...types.output_types import (
    AssistantMessage,
    FunctionCallOutputItem,
    OutputType,
    ProviderOutputItem,
    ReasoningOutputItem,
    TextOutputItem,
)
from ...types.request import Request
from ...types.response import AnthropicResponse, ResponseError
from ...types.streaming.event_types import (
    CustomProviderEvent,
    FunctionCallArgumentDeltaEvent,
    OutputItemCompletedEvent,
    ReasoningStartedEvent,
    ReasoningSummaryDeltaEvent,
    ReasoningTextDeltaEvent,
    ResponseCompletedEvent,
    ResponseStartedEvent,
    StreamEventUnion,
    TextDeltaEvent,
)
from ..adapter import (
    Adapter,
    FunctionToolResultProtocol,
    FunctionToolSchemaProtocol,
    ReasoningParamsProtocol,
    UserMessageProtocol,
)

class AnthropicAdapter(Adapter):
    def __init__(self, provider: AnthropicProvider):
        super().__init__(provider)
        self._client = provider.client

    def map_reasoning_params(self, reasoning: ReasoningParamsProtocol | None) -> dict | None:
        pass

    def  map_function_schema(self, tools: Sequence[FunctionToolSchemaProtocol]) -> list:

        _native_tools_list = []
        for tool in tools:
            _native_tool_schema: dict[str, object] = {}

            _native_tool_schema["type"] = "function"
            _native_tool_schema["name"] = tool.name
            _native_tool_schema["description"] = tool.description
            _native_tool_schema["strict"] = tool.strict if tool.strict is not None else True

            if tool.input_schema is not None:
                _native_tool_schema["parameters"] = self._native_tool_parameters(tool.input_schema) if tool.input_schema is not None else None

            canonical_keys = {
                "type",
                "name",
                "description",
                "strict",
                "parameters"
            }

            extra_fields = {
                key: value
                for key, value in tool.provider_options.items()
                if key not in canonical_keys
            }
            _native_tools_list.append({**extra_fields, **_native_tool_schema})
        return _native_tools_list



    def map_input_message(self, item: UserMessageProtocol):
        return {
            "role": item.role,
            "content": item.content
        }

    def _normalize_output_item(self, content_block) -> OutputType:

        match content_block.type:
            case "text":
                return TextOutputItem(
                        raw=content_block,
                        text=content_block.text
                    )

            # case "thinking":
            #     return ReasoningOutputItem(
            #         raw=output_item,
            #         id=output_item.id,
            #         content="".join(part.text for part in output_item.content),
            #         text="".join(part.text for part in output_item.summary)
            #     ) 

            # case "function_call":
            #     return FunctionCallOutputItem(
            #         raw=output_item,
            #         call_id=output_item.call_id,
            #         name=output_item.name,
            #         arguments=json.loads(output_item.arguments)
            #     )

            case _:
                raise ValueError(f"Unsupported Anthropic output item type: {content_block.type!r}")

    def _normalize_output(self, output_items) -> list[OutputType]:
        return [self._normalize_output_item(item) for item in output_items]

    def _build_request_kwargs(self, request: Request):
        if request.max_tokens is None:
            raise ValueError("max_tokens required for Anthropic requests.")
        
        canonical_params = {
            "model": request.model,
            "messages": request.input,
            "tools": self.map_function_schema(request.tools or []),
            "max_tokens": request.max_tokens
        }

        provider_options = dict(**request.provider_options or {})

        extra_body = provider_options.get("extra_body")

        if extra_body is not None:
            provider_options["extra_body"] = {
                key: value
                for key, value in extra_body.items()
                if key not in canonical_params
            }


        return {**provider_options, **canonical_params}


    def generate_sync(self, request: Request) -> AnthropicResponse:

        kwargs = self._build_request_kwargs(request)

        _raw_response = self._client.messages.create(**kwargs, stream=False)

        response = AnthropicResponse(
            id=_raw_response.id,
            provider=self._provider,
            model=request.model,
            output=self._normalize_output(_raw_response.content),
            raw_response=_raw_response
        )

        return cast(AnthropicResponse, response)

