from typing import Literal

from typing_extensions import Protocol


class Message(Protocol):
    ...

class UserMessageProtocol(Protocol):
    role: Literal["user"] = "user"
    content: str | list[dict]