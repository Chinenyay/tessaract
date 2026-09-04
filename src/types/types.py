from typing import Any, Literal
from typing_extensions import Protocol

from pydantic import BaseModel


class Message(Protocol):
    ...

class UserMessageProtocol(Protocol):
    role: Literal["user"] = "user"
    content: str | list[dict]