from typing import Any, Literal

from pydantic import BaseModel, Field

from ..providers.provider import Provider

from ..adapters.adapter import Adapter

from ..types.types import OutputItem

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

class AssistantMessage(BaseModel):
    type: Literal["assistant_message"] = "assistant_message"
    role: Literal["assistant"] = "assistant"
    content: list[TextOutputItem]
    raw: Any



# class OutputType(BaseModel):
#     raw: Any

class ReasoningOutputItem(OutputItem):
    type: Literal["reasoning"] = "reasoning"
    id: str | None = None
    text: str | list | None = None
    content: str | list | None = None

class ToolCallOutputItem(OutputItem):
    type: Literal["tool_call"] = "tool_call"
    call_id: str
    name: str
    arguments: str
