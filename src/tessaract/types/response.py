from dataclasses import dataclass, field
from typing import Any

from ..providers.openai_provider import OpenAIProvider
from ..providers.provider import Provider
from ..types.output_types import (
    AssistantMessage,
    OutputType,
    TextOutputItem,
)


@dataclass
class Response:
    id: str
    provider: Provider 
    model: str
    # status: ResponseStatus

    output: list[OutputType] = field(
        default_factory=list,
    )

    # usage: Usage | None = None
    # error: ResponseError | None = None

    # finish_details: FinishDetails | None = None

    # provider_timestamps: ProviderTimestamps | None = None
    # telemetry: ResponseTelemetry | None = None

    # provider_metadata: dict[str, Any] = Field(
    #     default_factory=dict,
    # )

    raw_response: Any | None = field(
        default=None,
        repr=False,
    )

    @property
    def output_text(self) -> str:
        return "".join(
            block.text
            for item in self.output
            if isinstance(item, AssistantMessage)
            for block in item.content
            if isinstance(block, TextOutputItem)
        )

    @property
    def response_id(self) -> str:
        return self.id


class OpenAIResponse(Response):
    provider: OpenAIProvider