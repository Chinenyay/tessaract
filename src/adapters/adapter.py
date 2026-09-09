from typing import Any, Literal

from typing_extensions import Protocol

from ..providers.provider import Provider

from ..tools.function import InputSchema


class UserMessageProtocol(Protocol):
    role: Literal["user"] = "user"
    content: str | list[dict]

class FunctionToolResultProtocol(Protocol):
    type: Literal["function_tool_result"] = "function_tool_result"
    call_id: str
    result: Any
    is_error: bool = False

class FunctionToolSchemaProtocol(Protocol):
    name: str
    description: str
    input_schema: InputSchema
    strict: bool | None = None
    # add a payload for non-common fields, like anthropic tool_examples

# class FunctionCallProtocol(Protocol):
#     type: Literal["tool_call"] = "tool_call"
#     call_id: str
#     name: str
#     arguments: str

class ReasoningParamsProtocol(Protocol):
    effort: Literal["none", "minimal", "low", "medium", "high", "extra_high", "max"] | None = None
    summary: Literal["concise", "auto", "detailed"] | None = None
    mode: Literal["standard", "pro"] | None = None

class ReasoningProtocol(Protocol):
    type: Literal["reasoning"] = "reasoning"
    text: str | None = None

class Adapter:
    def __init__(self, provider: Provider):
        self._provider = provider

    def map_input_message(self, item: UserMessageProtocol) -> Any:
        raise NotImplementedError("not yet implemented...")

    def map_tool_result(self, item: FunctionToolResultProtocol) -> Any:
        raise NotImplementedError("not yet implemented...")

    def map_function_schema(self, tools: list[FunctionToolSchemaProtocol]) -> list:
        raise NotImplementedError("not yet implemented...")

    def map_reasoning_params(self, item: ReasoningParamsProtocol) -> Any:
        raise NotImplementedError("not yet implemented...")
    
    def map_reasoning(self, item: ReasoningProtocol) -> Any:
        raise NotImplementedError("not yet implemented")



