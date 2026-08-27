from collections.abc import Sequence
from enum import Enum
from typing import Any, TypeAlias, Literal

from pydantic import BaseModel, Field

from .input_types import InputItemUnion, ToolCallResult
from .tools.function import FunctionTool
from .types import Provider, Role
from .output_types import OutputItemUnion


class Input(BaseModel):
    role: Role
    content: InputItemUnion

class Output(BaseModel):
    role: Role = "assistant"
    content: OutputItemUnion

class ProviderRequestOptions(BaseModel):
    type: Literal["provider_request"] = "provider_request"
    provider: Provider
    extra_body: dict[str, Any] = Field(default_factory=dict)

class ReasoningOptions(BaseModel):
    effort: Literal["minimal", "low", "medium", "high", "extra_high", "max"]

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
    input: list[Input | Output | ToolCallResult]
    tools: list[FunctionTool] | None = None
    reasoning:  ReasoningOptions | None = None
    stream: bool = False
    provider_options: ProviderRequestOptions | None = None










'''
OpenAI Request
model: str
input: List[InputItem]

InputItem:
    pass
    
role(InputItem):
    role: Literal["user" | "developer" | "system" | "assistant"]

content: List[ContentPart]

    background: Optional[bool]
    context_management: Optional[Iterable]
    conversation: Optional[Conversation]
    include: Optional[FesponseIncludable]
    *** input: Optional[Union[str, ResponseInputParam]] ***
    *** instructions: Optional[str] ***
    max_output_tokens: Optional[int]
    max_tool_calls: Optional[int]
    metadata: Optional[metadata]
    moderation: Optional[moderation]
    parallel_tool_calls: Optional[bool]
    *** previous_response_id: Optional[str] ***
    prompt: Optional[ResponsePromptParam]
    *** prompt_cache_key: Optional[str] ***
    *** prompt_cache_options: Optional[prompt_cache_options]
    *** reasoning: Optional[Reasoning] ****
    safety_identifier: Optional[str]
    service_tier: Optional[ServiceTier]
    store: Optional[bool]
    *** stream: Optional[Literal[false]] ***
    stream_options: Optional[StreamOptions]
    temperature: Optional[float]
    text: Optional[ResponseTextConfigurationParam]
        type: "json_schema" | "text" | "json_object" * older
    verbosity: Optional[Literal["low", "medium", "high"]]
    tool_choice: Optional[ToolChoice]
    *** tools: Optional[Iterable[ToolParam]] ***
    top_logprobs: Optional[int] = min(0), max(20)
    top_p: Optional[float]

BetaCacheControlEphemeral:
    type: Literal["ephemeral"]
    ttl: Literl["5m", "1h"]


PrompCacheOptions:
    mode: Literal["implicit", "explicit"]
    ttl: Literal["30m"]




Anthropic Request
    model: str
    max_tokens: int
    messages: list[Message]
    ** cache_control: Optional[BetaCacheControlEphemeral] **
    container: str | BetaContainerParam | None
    diagnostics: Optional[BetaDiagnosticsParam]
    context_management: Optional[BetaContextManagementConfig]
    fallback_credit_token
    fallbacks
    inference_geo: Optional[str]
    mcp_servers: BetaRequestMCPServerURLDefinition
    metadata: Optional[MetaData]
    speed: Optional[Literal["fast", "standard"]]
    service_tier: Optional[Literal["auto", "standard_only"]]
    stop_reason: BetaStopReason
    stop_details: BetaRefusalStopDetails
    stop_sequence: Optional[list[str]]
    stream: Optional[bool]
    tool_choice: Optional[BetaToolChoice]
    thinking: Optional[BetaThinkingConfigParam]
    tools: Optional[BetaToolUnion]
    output_format: Optional[BetaJSONOutputFormat]
    temperature: Optional[int] * deprecated
    top_k: Optional[int] * deprecated
    top_p: Optional[int] * deprecated





Message:
    role: "user" | "system" | "assistant"
    content: str | List[ContentBlock]

ContentBlock:
    pass

BetaCacheControlEphemeral:
    type: Literal["ephemeral"]
    ttl: Literal["5m" or "1h"]

TextBlock(ContentBlock):
    text: str
    type: Literal["text"]
    cache_control: BetaCacheControlEphemeral
    citations: Citation

ImageBlock
RequestDocumentBlock
SearchResultBlock
ThinkingBlock
RedactedThinkingBlock
ToolUseBlock
ServerToolUseBlock
WebSearchToolResultBlock
WebFetchToolResultBlock
AdvisorToolResultBlock
CodeExecutionToolResultBlock
BashCodeExecutionToolResultBlock
TextEditorCodeExecutionResultBlock
ToolSearchToolResultBlock
MCPToolUseBlock
RequestMCPToolResultBlock
ContainerUploadBlock
MidConversationSystemBlock
RequestToolAdditionBlock
RequestToolRemovalBlock
FallbackBlock





    






'''