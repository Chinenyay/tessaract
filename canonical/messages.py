from dataclasses import dataclass
from collections.abc import Iterable
from enum import Enum
from .input_types import ContentPart

class Role(Enum):
    user="user"
    assistant="assistant"
    system="system"
    developer="developer"


@dataclass(frozen=True)
class Message:
    role: str | Role
    content: Iterable[ContentPart]
