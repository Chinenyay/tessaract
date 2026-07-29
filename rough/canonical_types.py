from abc import ABC
from dataclasses import dataclass
from pydantic import BaseModel
from enum import Enum
import json
from typing import Optional

# from . import utils


''''
Data Types
    - Request
        - Inputs or Messages:
            - TextInput
            - ImageInput
            - Tools
            - ToolResult
            - FileInput
        - Roles:
            - User
            - Assistant
            - System
            - Developer

    - Response or Content
        - Response ID
        - Parts or Types:
            - OutputText
            - Reasoning
            - ToolCall
            - Metadata
    - Streaming
        - Response ID
        - Events:
            - Created
            - In Progress
            - Completed
            - Failed
            - Incomplete
        
        - Content:
            - Response
            - Output Item
            - Delta
            - Reasoning Summary
            - Reasoning Text
            - ToolCall
            - ImageGeneration
    - Error

Worker Types
    - Gateway: the client
    - Provider: the server
'''





# return dataclasses
@dataclass
class UsageBase:
    input_tokens: int
    cached_tokens: int | list
    cache_write_tokens: int
    output_tokens: int
    reasoning_tokens: int
    tessaract_computed_total_tokens: Optional[int] = None
    provider_reported_total_tokens: Optional[int] = None 

class OpenAIUsage(UsageBase):
    cached_tokens: int

class AnthropicUsage(UsageBase):
    cached_tokens: list[int]

type Usage = OpenAIUsage | AnthropicUsage # type alias for usage return type to do if isinstance(usage, AnthropicUsage) return AnthropicUsage

@dataclass
class ProviderMetadataBase:
    time_created: Optional[int]
    time_completed: Optional[int]
    metadata: Optional[dict]
    service_tier: str
    billing_payer: Optional[str]
    user: Optional[str]

class OpenAIMetadata(ProviderMetadataBase):
    pass

class AnthropicMetadata(ProviderMetadataBase):
    pass

type ProviderMetadata = OpenAIMetadata | AnthropicMetadata

@dataclass
class GenerationParams:
    log_probs: Optional[list]
    temperature: Optional[float]
    top_p: Optional[float]
    top_logprobs: Optional[int]
    frequency_penalty: Optional[float]
    presence_penalty: Optional[float]


# openai types for building message history
class HistoryMessageBlock(BaseModel):
    content: str
class User(HistoryMessageBlock):
    role: str = "user"


class Developer(HistoryMessageBlock):
    role: str = "developer"

class System(HistoryMessageBlock):
    role: str = "system"

class ToolResult(BaseModel):
    type: str = "function_call_output"
    call_id: str
    output: str



'''
openai function calling and execution (client side)
# tool call, when the model calls a custom tool, client side
{
"arguments": "{\"arg\":\"Aquarius\"}",
"call_id": "call_AMW2XSxSZiseYB0BLotYGxYI",
"name": "sample_tool",
"type": "function_call",
"id": "fc_0a3e4d88262234f3006a63681174f8819e87acb6c0ce2f7113",
"caller": null,
"namespace": null,
"status": "completed"
}

# tool call result, when the client application executes said tool and returns execution output to model
{
    "type": "function_call_output",
    "call_id": "call_AMW2XSxSZiseYB0BLotYGxYI",
    "output": "Aquarius: Next Tuesday you will befriend a baby otter."
}
crucially, the tool call result block call_id must be the same as the tool call id received from the api

# 
'''

class Tessaract:
    def __init__(self, providers: dict[str, object]):
        self.providers = providers

    




class JProvider(Provider):
    pass

class GatewayError(Exception):
    pass




    '''
Tessaract(
    providers={
        "openai": OpenAIProvider(api_key=..., base_url="),
        "anthropic": AnthropicProvider(api_key=...),
        'openai/gtp-5.5"
        /anthropic/opus-4
    }
    provider objects will take any arguments that can be provided to the native provider objects

    eg OpenAI(api_key, base_url, max_retries, default_headers?)
)

Gateway(
    providers=[
        OpenAI(...),
        Anthropic(...),
        OpenRouter(...),
        Ollama(...),
    ]
)
    '''