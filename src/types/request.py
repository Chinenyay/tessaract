from typing import Literal

from pydantic import BaseModel


class ReasoningOptions(BaseModel):
    effort: Literal["minimal", "low", "medium", "high", "extra_high", "max"] | None = None
    summary: Literal["concise", "auto", "detailed"] | None = None
    mode: Literal["standard", "pro"] | None = None

class Request(BaseModel):
    '''Request model for generating a response.
        Args:
            model: str
            instructions: str
            input: list[role | content]
            tools: list[FunctionTool] | None = None
            reasoning:  ReasoningOptions | None = None
            stream: bool = False
            provider_options: ProviderRequestOptions | None
    '''
    model: str
    instructions: str | None = None
    input: list
    # tools: list[FunctionTool] | None = None
    reasoning:  ReasoningOptions | None = None
    stream: bool = False
    # provider_options: ProviderRequestOptions | None = None
