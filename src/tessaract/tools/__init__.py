from .anthropic.bash import AnthropicBashTool
from .anthropic.computer_use import AnthropicComputerUseTool
from .openai.computer_use import OpenAIComputerUseToolCall
from .openai.shell import OpenAIHostedShellTool, OpenAILocalShellTool

type ShellTool = (AnthropicBashTool | OpenAILocalShellTool | OpenAIHostedShellTool)

type ComputerUse = (OpenAIComputerUseToolCall | AnthropicComputerUseTool)