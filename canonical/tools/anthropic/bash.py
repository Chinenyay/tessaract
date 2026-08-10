from typing import Literal

from ..shell import ClientExecutedShellTool


class AnthropicBashTool(ClientExecutedShellTool):
    provider: Literal["anthropic"] = "anthropic"
    type: Literal["bash_20250124"] = "bash_20250124"
    name: Literal["bash"]
