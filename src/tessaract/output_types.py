from typing import Any, Literal, TypeAlias

from pydantic import BaseModel, Field

from .types import Provider,  OutputItem



class Annotation(BaseModel):
    type: Literal["citation"] = "citation"

    source: str | None = None
    title: str | None = None
    cited_text: str | None = None

    provider: Provider
    provider_annotation_type: str

    provider_metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

class TextOutputItem(OutputItem):
    type: Literal["text"] = "text"
    text: str
    annotations: list[Annotation] = Field(
        default_factory=list,
    )

class Usage(BaseModel):
    input_tokens: int
    output_tokens: int

    total_tokens: int | None = None

    cached_input_tokens: int | None = None
    cache_write_input_tokens: int | None = None
    reasoning_tokens: int | None = None

class ReasoningOutputItem(OutputItem):
    type: Literal["reasoning"] = "reasoning"
    text: str | None = None
    encrypted_content: str | None = None
    signature: str | None = None


class ToolCallOutputItem(OutputItem):
    type: Literal["tool_call"] = "tool_call"
    call_id: str
    name: str
    arguments: str

class ProviderOutputItem(OutputItem):
    type: Literal["provider_output"] = "provider_output"
    provider: Provider
    provider_item_type: str
    data: dict[str, Any]

OutputItemUnion: TypeAlias = (TextOutputItem | ReasoningOutputItem | ToolCallOutputItem | ProviderOutputItem)

class IncompleteDetails(BaseModel):
    reason: str

class FinishDetails(BaseModel):
    reason: str
    provider_reason: str | None = None

class ResponseTelemetry(BaseModel):
    request_started_at: float
    first_token_at: float | None = None
    stream_completed_at: float | None = None
    time_to_first_token_ms: float | None = None

    raw_annotation: Any | None = Field(
        default=None,
        exclude=True,
        repr=False,
    )