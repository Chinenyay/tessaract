from openai.types.responses import (
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseReasoningItem
)

from ..providers.openai_provider import OpenAIProvider
from ..types.output_types import TextOutputItem, ReasoningOutputItem
from ..types.request import Request, ReasoningOptions
from ..types.response import OpenAIResponse
from ..types.types import UserMessageProtocol
from .adapter import Adapter


class OpenAIAdapter(Adapter):
    def __init__(self, provider: OpenAIProvider):
        super().__init__(provider)
        self._client = provider.client

    def map_input_message(self, item: UserMessageProtocol):
        return {
            "role": item.role,
            "content": item.content
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
            input=request.input,
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
