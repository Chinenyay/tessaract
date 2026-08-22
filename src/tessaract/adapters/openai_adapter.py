from openai import OpenAI
from openai.types.responses import EasyInputMessageParam

from ..input_types import (
    Text,
    FunctionToolCall,
    FunctionToolResult
)
from ..providers import OpenAIProvider
from ..request import Input, Request


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

        raise TypeError(f"Unsupported input part: {type(part).__name__}")

    def build_input(self, request: Request):
        input_list = []
        for item in request.input:
            openai_item = {
                "role": item.role,
                "content": [self._input_part(item.content)]
            }
            input_list.append(openai_item)
        return input_list
    
    def generate_sync(self, request: Request):
        response = self._client.responses.create(
            model=request.model,
            input=self.build_input(request=request),
        )

        return response
