from openai import OpenAI
from openai.types.responses import EasyInputMessageParam

from ..input_types import (
    Text,
    FunctionToolCall,
    FunctionToolResult
)
from ..request import Input, Request


class OpenAIAdapter:
    def __init__(self, request: Request, api_key: str):
        self._request = request
        self._api_key = api_key
        self._client = OpenAI(api_key=self._api_key)

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

    def build_input(self):
        input_list = []
        for item in self._request.input:
            openai_item = {
                "role": item.role,
                "content": [self._input_part(item.content)]
            }
            input_list.append(openai_item)
        return input_list
    
    def generate_sync(self):
        response = self._client.responses.create(
            model=self._request.model,
            input=self.build_input(),
        )
        return response
