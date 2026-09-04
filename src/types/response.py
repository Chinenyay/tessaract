from typing import Any, Literal

from dataclasses import dataclass, field
from ..providers.provider import Provider
from ..providers.openai_provider import OpenAIProvider
from ..types import Message, TextOutputItem

@dataclass
class Response:
    id: str
    provider: Provider 
    model: str
    # status: ResponseStatus

    output: list[Message] = field(
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
            item.text
            for item in self.output
            if isinstance(item, TextOutputItem)
        )

    @property
    def response_id(self) -> str:
        return self.id


class OpenAIResponse(Response):
    provider: OpenAIProvider