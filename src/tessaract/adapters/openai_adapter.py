from openai.types.responses import (
    ResponseFunctionToolCall,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseReasoningItem
)

from ..input_types import Text, ToolCallResult
from ..output_types import ReasoningOutputItem, TextOutputItem, ToolCallOutputItem
from ..providers import OpenAIProvider
from ..request import Output, Request, ReasoningOptions
from ..response import OpenAIResponse, ResponseStatus
from ..tools.function import FunctionTool, InputSchema


class OpenAIAdapter:
    def __init__(self, provider: OpenAIProvider):
        self._provider = provider
        self._client = self._provider.client

    def _input_part(self, part):
        if isinstance(part, str):
            return {
                "type": "input_text",
                "text": part
            }

        if isinstance(part, Text):
            return {
                "type": "input_text",
                "text": part.text
            }

        if isinstance(part, TextOutputItem):
            return {
                "type": "output_text",
                "text": part.text
            }
            

        raise TypeError(f"Unsupported input part: {type(part).__name__}")

    def build_input(self, request: Request):
        input_list = []
        for item in request.input:
            if isinstance(item, Output) and isinstance(item.content, ReasoningOutputItem):
                input_list.append(item.content.raw.model_dump())

            elif isinstance(item, Output) and isinstance(item.content, ToolCallOutputItem):
                openai_item = {
                    "type": "function_call",
                    "call_id": item.content.call_id,
                    "name": item.content.name,
                    "arguments": item.content.arguments
                }
                input_list.append(openai_item)

            elif isinstance(item, ToolCallResult):
                openai_item = {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": str(item.result)
                }
                input_list.append(openai_item)

            else:
                role = "assistant" if isinstance(item, TextOutputItem) else item.role
                content = item if isinstance(item, TextOutputItem) else item.content
                openai_item = {
                    "role": role,
                    "content": [self._input_part(content)]
                }
                input_list.append(openai_item)

        return input_list

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

            if isinstance(item, ResponseReasoningItem):
                tessaract_reasoning_item=ReasoningOutputItem(
                    raw=item,
                    encrypted_content=item.encrypted_content,
                    text="\n".join(summary.text for summary in item.summary)
                )
                _output_list.append(tessaract_reasoning_item)

            if isinstance(item, ResponseFunctionToolCall):
                tessaract_function_call=ToolCallOutputItem(
                    raw=item,
                    call_id=item.call_id,
                    name=item.name,
                    arguments=item.arguments
                )
                _output_list.append(tessaract_function_call)

        return _output_list

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
            "additionalProperties": input_schema.additionalProperties

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
    
    def _response_status(self, status: str):
        try:
            return ResponseStatus(status)
        except ValueError:
            raise ValueError(f"Unsupported response status {status}") from None

    def _native_reasoning_params(self, reasoning: ReasoningOptions | None = None):
        if reasoning is None:
            return None

        _summary = reasoning.summary if reasoning.summary else "auto"
        _reasoning_params = {}
        _effort = reasoning.effort if reasoning.effort else "none"
        if reasoning.mode:
            _reasoning_params["mode"] = reasoning.mode

        _reasoning_params["summary"] = _summary
        _reasoning_params["effort"] = _effort
        return _reasoning_params

        
    def generate_sync(self, request: Request):
        _raw_response = self._client.responses.create(
            model=request.model,
            input=self.build_input(request=request),
            tools=self._native_tools(request.tools),
            reasoning=self._native_reasoning_params(request.reasoning) 
        )

        response = OpenAIResponse(
            id=_raw_response.id,
            model=request.model,
            output=self._normalize_output(_raw_response.output),
            status=self._response_status(_raw_response.status),
            raw_response=_raw_response
        )

        return response

