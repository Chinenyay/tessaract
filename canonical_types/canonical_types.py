from abc import ABC, abstractmethod, abstractclassmethod
from dataclasses import dataclass
from enum import Enum
import json
from typing import Optional

from .utils import get_file_extension


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

@dataclass(frozen=True)
class Message(ABC):
    pass
    

@dataclass(frozen=True)
class Input(Message):
    @property
    def type(self):
        pass


@dataclass(frozen=True)
class TextInput(Input):
    content: str

    @property
    def type(self):
        return "input_text"

@dataclass(frozen=True)
class ImageInput(Input):
    path: str

    @property
    def type(self):
        return "image"

@dataclass(frozen=True)
class ToolObject:
    pass

@dataclass(frozen=True)
class ToolInput(Input):
    # tool attributes: name, description, type, parameters: type, description
    pass

    @property
    def type(self):
        pass


@dataclass(frozen=True)
class ToolCallResult(ToolInput):
    @property
    def type(self):
        return "tool_call_result"

@dataclass(frozen=True)
class ToolResultInput(ToolInput):

    @property
    def type(self):
        return "tool_result_input"

@dataclass
class FileInput:
    path: str

    @property
    def type(self):
        '''The canonical file type. All FileInput objects are input_file types by default.'''
        return "input_file"
    

    @property
    def filetype(self):
        '''Returns the file extension to identify the real file type'''
        ext = get_file_extension(self.path)
        return f"{ext}_input"

class Roles(Enum):
    user = "user"
    assistant = "assistant"
    system = "system"
    developer = "developer"

class Response(ABC):
    def __init__(self, raw_payload):
        self.raw_payload = raw_payload
    
    @property
    def payload(self):
        return self.raw_payload

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


class OpenAIResponse(Response):
    def __init__(self):
        self._payload_object = json.loads(self.raw_payload) # turns the raw payload from the provider API to a python dict object to avoid json <--> python type conflicts.

    @property
    def output_text(self):
        '''Returns final output text of the payload'''
        text = self.raw_payload["output"][0]["text"]
        return text
    
    @property
    def model(self):
        '''Model used to generate the response'''
        return self.raw_payload["model"]

    @property
    def response_id(self):
        return self.raw_payload["id"]

    @property
    def message_id(self):
        return self.raw_payload["output"][0]["id"]
    
    @property
    def previous_response_id(self):
        '''Returns None or the previous response id.'''
        return self._payload_object["previous_response_id"]

    @property
    def output_block(self):
        '''Returns all the content in the output block.'''
        return self.raw_payload["output"]
    
    @property
    def selected_tools(self):
        '''Tools the model has chosen to call'''
        return self.raw_payload["tools"]

    @property
    def time_data(self):
        pass
    
    @property
    def reasoning_block(self):
        return self._payload_object["reasoning"]
    
    @property
    def generation_parameters(self):
        p = self._payload_object
        log_probs = p["output"]["logprobs"]
        temperature = p["temperature"]
        top_p = p["top_p"]
        top_logprobs = p["top_logprobs"]
        frequency_penalty = p["frequency_penalty"]
        presence_penalty = p["presence_penalty"]

        return GenerationParams(
            log_probs=log_probs,
            temperature=temperature,
            top_p=top_p,
            top_logprobs=top_logprobs,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        ) 


    @property
    def prompt_cache_key(self):
        return self._payload_object["prompt_cache_key"]

    @property
    def token_usage(self):
        '''Number of tokens used by this response'''
        p = self._payload_object
        input_tokens = p["usage"]["input_tokens"]
        cached_tokens = p["usage"]["input_tokens_details"]["cached_tokens"]
        cache_write_tokens = p["usage"]["input_tokens_details"]["cache_write_tokens"]
        
        output_tokens = p["usage"]["output_tokens"]
        reasoning_tokens = p["usage"]["output_tokens_details"]["reasoning_tokens"]
        provider_reported_total_tokens = p["usage"]["total_tokens"]

        return OpenAIUsage(
            input_tokens=input_tokens,
            cached_tokens=cached_tokens,
            cache_write_tokens=cache_write_tokens,
            output_tokens=output_tokens,
            reasoning_tokens=reasoning_tokens,
            provider_reported_total_tokens=provider_reported_total_tokens
        )

    @property
    def provider_metadata(self):
        p = self._payload_object
        time_created = p["created_at"]
        time_completed = p["completed_at"]

        metadata = p["metadata"]
        service_tier = p["service_tier"]
        billing_payer = p["billing"]["payer"]
        user = p["user"]

        return OpenAIMetadata(
            time_created=time_created,
            time_completed=time_completed,
            metadata=metadata,
            service_tier=service_tier,
            billing_payer=billing_payer,
            user=user
        )
    
    @property
    def safety_moderation_metadata(self):
        p = self._payload_object        
        moderation = p["moderation"]
        safety_identifier = p["safety_identifier"]

        return (
            moderation,
            safety_identifier
        )

    @property
    def tessaract_telemetry_data(self):
        ''''Will collect metrics like time to first token, etc'''
        pass


class AnthropicResponse(Response):
    def __init__(self):
        self._payload_object = json.loads(self.raw_payload) # turns the raw payload from the provider API to a python dict object to avoid json <--> python type conflicts.

    @property
    def output_text(self):
        '''Returns final output text of the payload'''
        text = self.raw_payload["content"][0]["text"]
        return text
    
    @property
    def model(self):
        '''Model used to generate the response'''
        return self.raw_payload["model"]

    @property
    def response_id(self):
        return self.raw_payload["id"]

    @property
    def output_block(self):
        '''Returns all the content in the output block.'''
        return self.raw_payload["content"]
    
    @property
    def selected_tools(self):
        '''Tools the model has chosen to call'''
        return self.raw_payload["tools"]

    @property
    def time_data(self):
        pass
    
    @property
    def reasoning_block(self):
        read_block = self._payload_object()["content"]
        write_block = []
        for bl in read_block:
            if bl["type"] == "thinking":
                write_block.append(bl)
        return read_block

    @property
    def token_usage(self):
        '''Number of tokens used by this response'''
        p = self._payload_object
        input_tokens = p["usage"]["input_tokens"]
        cached_tokens: list[int] = p["usage"]["cache_creation"]
        cache_write_tokens = p["usage"]["input_tokens_details"]["cache_write_tokens"]
        
        output_tokens = p["usage"]["output_tokens"]
        reasoning_tokens = p["usage"]["output_tokens_details"]["reasoning_tokens"]
        tessaract_computed_total_tokens = input_tokens + output_tokens

        return Usage(
            input_tokens=input_tokens,
            cached_tokens=cached_tokens,
            cache_write_tokens=cache_write_tokens,
            output_tokens=output_tokens,
            reasoning_tokens=reasoning_tokens,
            tessaract_computed_total_tokens=tessaract_computed_total_tokens,
        )

    @property
    def provider_metadata(self):
        p = self._payload_object
        time_created = p["created_at"]
        time_completed = p["completed_at"]

        metadata = p["metadata"]
        service_tier = p["service_tier"]
        billing_payer = p["billing"]["payer"]
        user = p["user"]

        return (
            time_created,
            time_completed,
            metadata,
            service_tier,
            billing_payer,
            user
        )
    
    @property
    def safety_moderation_metadata(self):
        p = self._payload_object        
        moderation = p["moderation"]
        safety_identifier = p["safety_identifier"]

        return (
            moderation,
            safety_identifier
        )

    @property
    def tessaract_telemetry_data(self):
        ''''Will collect metrics like time to first token, etc'''
        pass








class Tesseract:
    pass

class Provider:
    pass

class GatewayError:
    pass

class Stream:
    pass
