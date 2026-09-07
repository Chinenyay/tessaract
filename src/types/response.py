from dataclasses import dataclass, field
from typing import Any

from ..providers.openai_provider import OpenAIProvider
from ..providers.provider import Provider
from ..types.types import OutputItem
from ..types.output_types import ReasoningOutputItem, TextOutputItem


@dataclass
class Response:
    id: str
    provider: Provider 
    model: str
    # status: ResponseStatus

    output: list[OutputItem] = field(
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
            item.content.text
            for item in self.output
            if isinstance(item, TextOutputItem)
        )

    @property
    def reasoning(self) -> str:
        return "".join(
            item.text
            for item in self.output
            if isinstance(item, ReasoningOutputItem)
            and item.text is not None
        )
    
    @property
    def response_id(self) -> str:
        return self.id


class OpenAIResponse(Response):
    provider: OpenAIProvider