from typing import Literal

from pydantic import BaseModel

from .input_types import (
    AudioPart,
    FilePart,
    FunctionToolCallPart,
    ImagePart,
    TextPart,
    role,
)
from .output_types import ReasoningOutputItem
from .tools.function import FunctionTool

content = TextPart | ImagePart | AudioPart | FilePart | FunctionToolCallPart


class Request(BaseModel):
    model: str
    messages: list[role | content]
    tools: list[FunctionTool] | None = None
    reasoning: ReasoningOutputItem | None = None
    previous_response_id: str | None = None
    stream: bool = False








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
    prompt_cache_options: Optional[prompt_cache_options]
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