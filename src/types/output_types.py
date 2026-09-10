from typing import Any, Literal, TypeAlias

from pydantic import BaseModel, Field

from ..providers.provider import Provider

from ..adapters.adapter import Adapter



class OutputItem(BaseModel):
    raw: Any

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

class AssistantMessage(OutputType):
    type: Literal["assistant_message"] = "assistant_message"
    role: Literal["assistant"] = "assistant"
    content: list[TextOutputItem]
    raw: Any

class ReasoningOutputItem(OutputItem):
    type: Literal["reasoning"] = "reasoning"
    id: str | None = None
    text: str | list | None = None
    content: str | list | None = None

class FunctionCallOutputItem(OutputItem):
    type: Literal["function_call"] = "function_call"
    call_id: str
    name: str
    arguments: str

OutputType: TypeAlias = AssistantMessage | ReasoningOutputItem | FunctionCallOutputItem | TextOutputItem