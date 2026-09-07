from openai.types.responses import (
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseReasoningItem
)

from ..providers.openai_provider import OpenAIProvider
from ..types.output_types import TextOutputItem, ReasoningOutputItem
from ..types.request import Request, ReasoningOptions
from ..types.response import OpenAIResponse
from ..tools.function import InputSchema, FunctionTool
from .adapter import Adapter, UserMessageProtocol, ToolResultProtocol


class OpenAIAdapter(Adapter):
    def __init__(self, provider: OpenAIProvider):
        super().__init__(provider)
        self._client = provider.client

    def map_input_message(self, item: UserMessageProtocol):
        return {
            "role": item.role,
            "content": item.content
        }

    def map_tool_result(self, item: ToolResultProtocol):
        return {
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": item.result
        }

    def _normalize_output(self, output_items):
        _output_list = []

        for item in output_items:
            if isinstance(item, ResponseOutputMessage):
                content = item.content
                for item in content:
                    if isinstance(item, ResponseOutputText):
                        tessaract_output_text=TextOutputItem(
                            text=item.text,
                            annotations=item.annotations,
                            raw=item
                        )
                        _output_list.append(tessaract_output_text)

            elif isinstance(item, ResponseReasoningItem):
                tessaract_reasoning_text=ReasoningOutputItem(
                    raw=item,
                    text="\n".join(summary.text for summary in item.summary)
                )
                _output_list.append(tessaract_reasoning_text)

        return _output_list

    def _native_reasoning_params(self, reasoning: ReasoningOptions | None = None):
        if reasoning is None:
            return None

        _reasoning_params: dict[str, str] = {}

        if reasoning.mode is not None:
            _reasoning_params["mode"] = reasoning.mode

        if reasoning.summary is not None:
            _reasoning_params["summary"] = reasoning.summary

        if reasoning.effort is not None:
            _reasoning_params["effort"] = (
                "xhigh" if reasoning.effort == "extra_high" else reasoning.effort
            )

        return _reasoning_params

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

    def _native_tools(self, tools: list[FunctionTool]):
        _native_tools_list = []
        for tool in tools:
            _native_tool_schema = {
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": self._native_tool_parameters(tool.input_schema),
                "strict": tool.strict if tool.strict is not None else True
            }
            _native_tools_list.append(_native_tool_schema)
        return _native_tools_list


    def generate_sync(self, request: Request):
        _raw_response = self._client.responses.create(
            model=request.model,
            input=request.input,
            tools=self._native_tools(request.tools),
            reasoning=self._native_reasoning_params(request.reasoning)
        )

        response = OpenAIResponse(
            id=_raw_response.id,
            provider=self._provider,
            model=request.model,
            output=self._normalize_output(_raw_response.output),
            raw_response=_raw_response
        )

        return response
