from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .messages import Message
from .stream import ResponseError

Provider = Literal["anthropic", "openai"]

ResponseStatus = Literal[
    "queued",
    "in_progress",
    "completed",
    "incomplete",
    "failed",
    "cancelled"
]


class TextOutputItem(BaseModel):
    pass

class ReasoningOutputItem(BaseModel):
    pass

class ToolCallOutputItem(BaseModel):
    pass

class ProviderOutputItem(BaseModel):
    pass

OutputItem = (
    TextOutputItem,
    ReasoningOutputItem,
    ToolCallOutputItem,
    ProviderOutputItem
)

class Response(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
    )

    id: str
    provider: Provider
    model: str
    status: ResponseStatus

    output: list[OutputItem] = Field(
        default_factory=list,
    )

    usage: "Usage | None" = None
    error: ResponseError | None = None

    finish_reason: str | None = None
    stop_sequence: str | None = None

    created_at: float | None = None
    completed_at: float | None = None

    provider_metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    raw_response: Any | None = Field(
        default=None,
        exclude=True,
        repr=False
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


