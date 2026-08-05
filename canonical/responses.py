from typing import Any, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from .output_types import OutputItem, TextOutputItem
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


