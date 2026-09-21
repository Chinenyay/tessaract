import json
from collections.abc import Iterator, Sequence
from typing import cast

from openai import Omit
from openai.types.shared_params import Reasoning as OpenAIReasoningParams

from ...providers.openai_provider import OpenAIProvider
from ...tools.function import InputSchema
from ...types.output_types import (
    AssistantMessage,
    FunctionCallOutputItem,
    ProviderOutputItem,
    OutputType,
    ReasoningOutputItem,
    TextOutputItem,
)
from ...types.request import Request
from ...types.response import OpenAIResponse, ResponseError
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

        
    def _normalize_output_item(self, output_item) -> OutputType:
        if output_item.type == "message" and (
            output_item.content is None or any(
                part.type != "output_text"
                or bool(getattr(part, "annotations", []))
                for part in output_item.content
            )
        ):
            return ProviderOutputItem(raw=output_item, provider_type=output_item.type)
        
        match output_item.type:
            case "message":
                return AssistantMessage(
                        raw=output_item,
                        content=[
                            TextOutputItem(
                                raw=i,
                                text=i.text,
                                annotations=i.annotations
                            )
                            for i in output_item.content
                        ]
                    )

            case "reasoning":
                return ReasoningOutputItem(
                    raw=output_item,
                    id=output_item.id,
                    content="".join(part.text for part in output_item.content),
                    text="".join(part.text for part in output_item.summary)
                ) 

            case "function_call":
                return FunctionCallOutputItem(
                    raw=output_item,
                    call_id=output_item.call_id,
                    name=output_item.name,
                    arguments=json.loads(output_item.arguments)
                )

            case _:
                raise ValueError(f"Unsupported OpenAI output item type: {output_item.type!r}")


    def _normalize_output(self, output_items) -> list[OutputType]:
        return [self._normalize_output_item(item) for item in output_items]

    def _normalize_stream_event(self, event):
        match event.type:
            case "response.created":
                yield ResponseStartedEvent(
                    raw_event=event
                )

            case "response.completed":
                yield ResponseCompletedEvent(
                    response=OpenAIResponse(
                        id=event.response.id,
                        model=event.response.model,
                        status=event.response.status,
                        output=self._normalize_output(event.response.output),
                        error=ResponseError(message=event.response.error.message) if event.response.error else None,
                        raw_response=event.response
                        ),
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

            case "response.output_item.done":
                yield OutputItemCompletedEvent(
                    item=self._normalize_output_item(event.item),
                    raw_event=event
                )

            case "response.reasoning_summary_text.delta":
                yield ReasoningSummaryDeltaEvent(
                    delta=event.delta,
                    output_index=event.output_index,
                    item_id=event.item_id,
                    raw_event=event
                )

            case "response.reasoning_text.delta":
                yield ReasoningTextDeltaEvent(
                    delta=event.delta,
                    output_index=event.output_index,
                    item_id=event.item_id,
                    raw_event=event
                )

            case "response.function_call_arguments.delta":
                yield FunctionCallArgumentDeltaEvent(
                    delta=event.delta,
                    output_index=event.output_index,
                    raw_event=event
                )

            case "response.reasoning_summary_part.added":
                yield ReasoningStartedEvent(
                    item_id=event.item_id,
                    raw_event=event
                )

            case _:
                yield CustomProviderEvent(
                    type=event.type,
                    raw_event=event
                )


    def _build_request_kwargs(self, request: Request):
        canonical_params = {
            "model": request.model,
            "input": request.input,
            "tools": self.map_function_schema(request.tools or []),
            "reasoning": self.map_reasoning_params(request.reasoning), 
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
