
from typing import Any, TypeAlias, Literal

from pydantic import BaseModel

from .types import Message

class ContentPart(BaseModel):
    pass

class Text(ContentPart):
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

class Image(ContentPart):
    source: MediaSource

class File(ContentPart):
    source: MediaSource

class Audio(ContentPart):
    source: MediaSource


class FunctionToolCall(ContentPart):
    type: Literal["tool_call"] = "tool_call"
    call_id: str
    name: str
    arguments: str


class FunctionToolResult(ContentPart):
    type: Literal["function_tool_result"] = "function_tool_result"
    call_id: str
    result: Any
    is_error: bool = False

InputItemUnion: TypeAlias = ( str| Text | Image | Audio | File | FunctionToolCall | FunctionToolResult)


class UserMessage(Message):
    role: Literal["user"] = "user"
    content: str | Text | File | Audio | Image | FunctionToolCall | FunctionToolResult



