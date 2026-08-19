from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

Provider = Literal["anthropic", "openai"]

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

class ResponseTelemetry(BaseModel):
    request_started_at: datetime
    response_started_at: datetime | None = None
    first_token_at: datetime | None = None
    response_finished_at: datetime | None = None