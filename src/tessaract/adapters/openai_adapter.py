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

    def _content_part(self, part):
        if isinstance(part, TextPart):
            return ResponseInputTextContentParam(
                type="input_text"
            )
            # return {"type": "input_text", "text": part.text}

        raise ValueError(f"unsupported content part: {type(part).__name__}")

    def _input_item(self, item: Input):
        role = item.role

        if isinstance(item.content, FunctionToolCallPart):
            return {
                "type": "function_call",
                "call_id": item.content.call_id,
                "name": item.content.name,
                "arguments": item.content.arguments
            }

        if isinstance(item.content, FunctionToolResult):
            return {
                "type": "function_call_output",
                "call_id": item.content.call_id,
                "output": str(item.content.result),
            }

        if isinstance(item.content, TextPart):
            return {
                "type": "input_text",
                "text": item.content.text
            }


    def normalize_request(self):
        raw = self._request.input

        if raw is None:
            return []

        if isinstance(raw, str):
            return raw

        return self._input_item(raw)

    

    def generate_sync(self):
        response = self._client.responses.create(
            model=self._request.model,
            input=self.normalize_request(),
        )
        