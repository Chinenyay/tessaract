from .anthropic.anthropic import AnthropicBashTool
from .openai.shell import OpenAIHostedShellTool, OpenAILocalShellTool

type ShellTool = AnthropicBashTool | OpenAILocalShellTool | OpenAIHostedShellTool
