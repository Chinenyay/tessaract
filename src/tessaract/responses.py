from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .output_types import OutputItem, TextOutputItem, Usage
from .types import FinishDetails, Provider, ResponseTelemetry


class ResponseStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResponseError(BaseModel):
    message: str
    code: str | None = None


class ProviderTimestamps(BaseModel):
    created_at: float | None = None
    completed_at: float | None = None

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

    finish_details: FinishDetails | None = None

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
    provider: Literal["anthropic"] = "anthropic"

    @property
    def container(self) -> object | None:
        raw = self.raw_response
        if raw is None:
            return None
        return raw.container

    @property
    def inference_geo(self) -> str | None:
        raw = self.raw_response
        if raw is None:
            return None
        return raw.usage.inference_geo
