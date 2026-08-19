
from typing import Any, Literal

from pydantic import BaseModel

from .types import Provider

role = Literal["user", "assistant", "system", "developer"]

class ContentPart(BaseModel):
    pass

class TextPart(ContentPart):
    text: str


class URLSource(BaseModel):
    url: str
    media_type: str | None = None


class ByteSource(BaseModel):
    bytes: str
    media_type: str | None = None

class ProviderFileSource(BaseModel):
    provider: str
    file_id: str
    media_type: str | None = None

MediaSource = URLSource | ByteSource | ProviderFileSource

class ImagePart(ContentPart):
    source: MediaSource

class FilePart(ContentPart):
    source: MediaSource

class AudioPart(ContentPart):
    source: MediaSource


class FunctionToolCallPart(ContentPart):
    type: Literal["tool_call"] = "tool_call"
    call_id: str
    name: str
    arguments: str


class FunctionToolResult(ContentPart):
    type: Literal["function_tool_result"] = "function_tool_result"
    call_id: str
    result: Any
    is_error: bool = False


