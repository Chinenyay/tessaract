from typing import Any, Literal

from typing_extensions import Protocol

from ..providers.provider import Provider


class UserMessageProtocol(Protocol):
    role: Literal["user"] = "user"
    content: str | list[dict]

class ToolResultProtocol(Protocol):
    type: Literal["tool_result"] = "tool_result"
    call_id: str
    result: Any
    is_error: bool = False

class Adapter:
    def __init__(self, provider: Provider):
        self._provider = provider

    def map_input_message(self, item: UserMessageProtocol) -> Any:
        raise NotImplementedError("not yet implemented...")

    def map_tool_result(self, item: ToolResultProtocol) -> Any:
        raise NotImplementedError("not yet implemented...")