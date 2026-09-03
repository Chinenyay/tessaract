from typing import Any, Literal
from typing_extensions import Protocol

from pydantic import BaseModel


class Message(BaseModel):
    raw: Any

class InputMessageProtocol(Protocol):
    role: str
    content: str | list[dict]

