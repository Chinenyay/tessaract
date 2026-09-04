from typing import Any, Literal
from typing_extensions import Protocol

from pydantic import BaseModel

from ..providers.provider import Provider
#from ..types.types import UserMessageProtocol

class UserMessageProtocol(Protocol):
    role: Literal["user"] = "user"
    content: str | list[dict]

class Adapter:
    def __init__(self, provider: Provider):
        self._provider = provider

    def map_input_message(self, item: UserMessageProtocol) -> Any:
        raise NotImplementedError("not yet implemented...")