from enum import Enum
from typing import Any, Literal, TypeAlias
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .output_types import OutputItem, TextOutputItem, Usage

Provider = Literal["anthropic", "openai"]

class ResponseStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FinishReason(str, Enum):
    COMPLETED = "completed"
    STOP_SEQUENCE = "stop_sequence"
    TOOL_CALL = "tool_call"
    MAX_TOKENS = "max_tokens"
    CONTEXT_LIMIT = "context_limit"
    CONTENT_FILTER = "content_filter"
    REFUSAL = "refusal"
    PAUSED = "paused"
    UNKNOWN = "unknown"


class FinishDetails(BaseModel):
    reason: FinishReason
    provider_reason: str | None = None
    stop_sequence: str | None = None

    termination_metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

class ResponseError(BaseModel):
    message: str
    code: str | None = None


class ProviderTimestamps(BaseModel):
    created_at: float | None = None
    completed_at: float | None = None

class ResponseTelemetry(BaseModel):
    request_started_at: datetime
    response_started_at: datetime | None = None
    first_token_at: datetime | None = None
    response_finished_at: datetime | None = None

    @property
    def time_to_first_token_seconds(self):
        if self.first_token_at is None:
            return None

        return (
            self.first_token_at - self.request_started_at
        ).total_seconds()

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

    usage: Usage | None = None
    error: ResponseError | None = None

    finish_details: FinishDetails

    provider_timestamps: ProviderTimestamps | None = None
    telemetry: ResponseTelemetry | None = None

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

class OpenAIResponse(Response):
    provider: Literal["openai"] = "openai"

    @property
    def previous_response_id(self) -> str | None:
        raw = self.raw_response
        if raw is None:
            return None
        return raw.previous_response_id

    @property
    def conversation_id(self) -> str | None:
        raw = self.raw_response
        if raw is None or raw.conversation is None:
            return None
        return raw.conversation.id

    @property
    def service_tier(self):
        raw = self.raw_response
        if raw is None:
            return None
        return raw.service_tier


class AnthropicResponse(Response):
    pass