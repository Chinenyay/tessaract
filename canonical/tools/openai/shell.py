from typing import Literal

from ..shell import ClientExecutedShellTool, ProviderExecutedShellTool
from .environment import Environment


class OpenAIHostedShellTool(ProviderExecutedShellTool):
    type: Literal["shell"] = "shell"
    environment: Environment
    # TODO: add skills_reference object

class OpenAILocalShellTool(ClientExecutedShellTool):
    provider: Literal["openai"] = "openai"
    type: Literal["shell"] = "shell"
    environment: Literal["local"]
