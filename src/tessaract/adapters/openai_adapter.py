from collections.abc import Sequence
from typing import cast

from openai import Omit
from openai.types.shared_params import Reasoning as OpenAIReasoningParams

from ..providers.openai_provider import OpenAIProvider
from ..tools.function import InputSchema
from ..types.output_types import (
    AssistantMessage,
    FunctionCallOutputItem,
    OutputType,
    ReasoningOutputItem,
    TextOutputItem,
)
from ..types.request import Request
from ..types.response import OpenAIResponse
from .adapter import (
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
            "additionalProperties": input_schema.additionalProperties if not None else False
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

            _native_tools_list.append(_native_tool_schema)
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
                        arguments=item.arguments
                    )
                )

        return _output_list


    def generate_sync(self, request: Request) -> OpenAIResponse:
        _raw_response = self._client.responses.create(
            model=request.model,
            input=request.input,
            tools=self.map_function_schema(request.tools or []),
            reasoning=self.map_reasoning_params(request.reasoning)
        )

        response = OpenAIResponse(
            id=_raw_response.id,
            provider=self._provider,
            model=request.model,
            output=self._normalize_output(_raw_response.output),
            raw_response=_raw_response
        )

        return cast(OpenAIResponse, response)
