from openai import OpenAI
from openai.types.responses import EasyInputMessageParam, ResponseOutputMessage, ResponseOutputText

from ..tools.function import FunctionTool
from ..input_types import (
    Text,
    FunctionToolCall,
    FunctionToolResult
)
from ..providers import OpenAIProvider
from ..request import Input, Request
from ..response import Response, OpenAIResponse, ResponseStatus
from ..output_types import TextOutputItem


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

            if isinstance(item, FunctionToolCall):
                

        return _output_list

    def _native_tools(self, tools: list[FunctionTool]):
        _native_tools_list = []
        for tool in tools:
            _native_tool_schema = {
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema,
                "strict": tool.strict if tool.strict is not None else True
            }
            _native_tools_list.append(_native_tool_schema)
        return _native_tools_list
    
    def _response_status(self, status: str):
        try:
            return ResponseStatus(status)
        except ValueError:
            raise ValueError(f"Unsupported response status {status}") from None


    def generate_sync(self, request: Request):
        _raw_response = self._client.responses.create(
            model=request.model,
            input=self.build_input(request=request),
            tools=self._native_tools(request.tools)
        )

        response = OpenAIResponse(
            id=_raw_response.id,
            model=request.model,
            output=self._normalize_output(_raw_response.output),
            status=self._response_status(_raw_response.status),
            raw_response=_raw_response
        )


        return response
