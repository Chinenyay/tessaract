from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from .input_types import ContentPart


@dataclass(frozen=True)
class ToolCallPart(ContentPart):
    pass

type JSONSchema = Mapping[str, Any]

class FunctionTool(ContentPart):
    name: str
    description: str
    input_schema: JSONSchema

class ToolResult(ContentPart):
    pass



class ProviderTool:
    pass

class ProviderExecutedTool(ProviderTool):
    pass

class ClientExecutedProviderTool(ProviderTool):
    pass


class ClientExecutedShellTool(ClientExecutedProviderTool):
    pass
    
class OpenAIHostedShellTool(ClientExecutedShellTool):
    provider: Literal["openai"] = "openai"
    type: Literal["shell"] = "shell"
    environment: Literal["local"]


class AnthropicHostedShellTool(ClientExecutedShellTool):
    provider: Literal["anthropic"] = "anthropic"
    type: Literal["bash_20250124"] = "bash_20250124"
    name: Literal["bash"]

ShellTool = ClientExecutedShellTool | "ProviderExecutedShellTool"

