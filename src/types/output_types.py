from typing import Any, Literal

from pydantic import BaseModel, Field

from ..providers.provider import Provider

from .types import Message

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


class AssistantMessage(Message):
    role: Literal["assistant"] = "assistant"
    raw: Any 


class TextOutputItem(AssistantMessage):
    type: Literal["text"] = "text"
    text: str
    annotations: list[Annotation] = Field(
        default_factory=list,
    )
