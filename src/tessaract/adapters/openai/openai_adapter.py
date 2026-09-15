import json
from collections.abc import Iterator, Sequence
from typing import cast
from contextlib import contextmanager

from openai import Omit, Stream
from openai.types.responses import ResponseStreamEvent
from openai.types.shared_params import Reasoning as OpenAIReasoningParams

from ...providers.openai_provider import OpenAIProvider
from ...tools.function import InputSchema
from ...types.output_types import (
    AssistantMessage,
    FunctionCallOutputItem,
    OutputType,
    ReasoningOutputItem,
    TextOutputItem,
)
from ...types.request import Request
from ...types.response import OpenAIResponse
from ..adapter import (
    Adapter,
    FunctionToolResultProtocol,
    FunctionToolSchemaProtocol,
    ReasoningParamsProtocol,
    UserMessageProtocol,
)
from ...types.streaming.event_types import (
    ResponseStartedEvent,
    ResponseCompletedEvent,
    TextDeltaEvent,
    CustomProviderEvent,
    StreamEventUnion
)


class OpenAIAdapter(Adapter):
    def __init__(self, provider: OpenAIProvider):
        super().__init__(provider)
        self._client = provider.client

    def map_input_message(self, item: UserMessageProtocol):
        return {
            "role": item.role,
            "content": item.content
        }

    def map_reasoning_params(self, reasoning: ReasoningParamsProtocol | None) -> OpenAIReasoningParams | Omit | None:
        if reasoning is None:
            return Omit()

        native_reasoning: OpenAIReasoningParams = {}

        if reasoning.mode is not None:
            native_reasoning["mode"] = reasoning.mode

        if reasoning.summary is not None:
            native_reasoning["summary"] = reasoning.summary

        if reasoning.effort is not None:
            native_reasoning["effort"] = (
                "xhigh" if reasoning.effort == "extra_high" else reasoning.effort
            )

        return native_reasoning

    def _native_tool_parameters(self, input_schema: InputSchema):
        _properties = {}
        for prop_name, prop_schema in input_schema.properties.items():
            _properties[prop_name] = {
                    "type": prop_schema.type,
                    "description": prop_schema.description
                }

        return {
            "type": input_schema.type,
            "properties": _properties,
            "required": input_schema.required,
            "additionalProperties": input_schema.additionalProperties if input_schema.additionalProperties is not None else False
        }

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

    def map_tool_result(self, item: FunctionToolResultProtocol):
        return {
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": item.result
        }

    def _normalize_output(self, output_items) -> list[OutputType]:
        _output_list: list[OutputType] = []

        for item in output_items:
            if item.type == "message":
                _output_list.append(
                    AssistantMessage(
                        raw=item,
                        content=[
                            TextOutputItem(
                                raw=i,
                                text=i.text,
                                annotations=i.annotations
                            )
                            for i in item.content
                        ]
                    )
                )
    
            elif item.type == "reasoning":
                _output_list.append(
                    ReasoningOutputItem(
                        raw=item,
                        id=item.id,
                        content="".join(part.text for part in item.content),
                        text="".join(part.text for part in item.summary)
                    )
                )
                
            elif item.type == "function_call":
                _output_list.append(
                    FunctionCallOutputItem(
                        raw=item,
                        call_id=item.call_id,
                        name=item.name,
                        arguments=json.loads(item.arguments)
                    )
                )

        return _output_list

    def _normalize_stream_event(self, event):
        match event.type:
            case "response.created":
                yield ResponseStartedEvent(
                    raw_event=event
                )

            case "response.completed":
                yield ResponseCompletedEvent(
                    raw_event=event
                )

            case "response.output_text.delta":
                yield TextDeltaEvent(
                    delta=event.delta,
                    provider="openai",
                    output_index=event.output_index,
                    content_index=event.content_index,
                    raw_event=event
                )

            case _:
                yield CustomProviderEvent(
                    raw_event=event
                )
        

    def _build_request_kwargs(self, request: Request):
        canonical_params = {
            "model": request.model,
            "input": request.input,
            "tools": self.map_function_schema(request.tools or []),
            "reasoning": self.map_reasoning_params(request.reasoning), 
        }

        provider_options = dict(**request.provider_options or {})  # noqa: F841

        extra_body = provider_options.get("extra_body")

        if extra_body is not None:
            provider_options["extra_body"] = {
                key: value
                for key, value in extra_body.items()
                if key not in canonical_params
            }


        return {**provider_options, **canonical_params}

    def generate_sync(self, request: Request) -> OpenAIResponse:

        kwargs = self._build_request_kwargs(request)

        _raw_response = self._client.responses.create(**kwargs, stream=False)

        response = OpenAIResponse(
            id=_raw_response.id,
            status=_raw_response.status,
            provider=self._provider,
            model=request.model,
            output=self._normalize_output(_raw_response.output),
            raw_response=_raw_response
        )

        return cast(OpenAIResponse, response)

    def generate_stream(self, request: Request) -> Iterator[StreamEventUnion]:
    
        kwargs = self._build_request_kwargs(request)

        with self._client.responses.stream(**kwargs) as stream:
            for raw_event in stream:
                yield from self._normalize_stream_event(raw_event)


