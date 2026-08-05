from typing import Any, Literal

from pydantic import BaseModel, Field

from .responses import Response


class TextDeltaEvent(BaseModel):
    type: Literal["text.delta"] = "text.delta"

    delta: str

    provider: Literal["openai", "anthropic"]
    response_id: str | None = None

    output_index: int | None = None
    content_index: int | None = None
    item_id: str | None = None

    raw_event: object | None = None

class ResponseStartedEvent(BaseModel):
    type: Literal["response_started"] = "response_started"
    response: Response

    raw_event: Any = Field(
        exclude=True,
        repr=False
    )

class ResponseCompletedEvent(BaseModel):
    type: Literal["response.completed"] = "response.completed"
    response: Response

    raw_event: Any = Field(
        exclude=True,
        repr=False
    )

class ReasoningDeltaEvent(BaseModel):
    type: Literal["reasoning.delta"] = "reasoning.delta"
    item_id: str | None = None
    delta: str
    output_index: int
    content_index: int | None = None

    raw_event: Any | None = Field(
        default=None,
        exclude=True,
        repr=False
    )

class ToolArgumentsDeltaEvent(BaseModel):
    type: Literal["tool_arguments.delta"] = "tool_arguments.delta"
    item_id: str | None = None
    delta: str
    output_index: int
    content_index: int | None = None
    
    raw_event: Any | None = Field(
        default=None,
        exclude=True,
        repr=False
    )

class ToolCallStartedEvent(BaseModel):
    type: Literal["tool_call.started"] = "tool_call.started"

    call_id: str
    name: str
    output_index: int

    raw_event: Any | None = Field(
        default=None,
        exclude=True,
        repr=False,
    )


'''
=========Tessaract Canonical Streaming Types=============

DONE ToolCallStartedEvent -> ant: content_block_start, content_block_type: tool_use, oai: response.output_item.added, output_item.type: fuction_call
    oai
    object: response.output_item.added
    event_type: "response.output_item.added"
    properties:
        type: Literal["response.output_item.added"]
        output_index: int
        item: object
        sequence_number: int

    ant
    object: 

DONE ToolArgumentsDeltaEvent -> ant: input_json_delta, oai: response.function_call_arguments.delta
    oai:
        object: response.function_call_arguments.delta
        event_type: "response.function_call_arguments.delta"

        properties:
            type: Literal["response.function_call_arguments.delta"]
            item_id: str
            output_index: int
            delta: str
            sequence_number: str
    
    ant:
        object: RawContentBlockDeltaEvent
        event_type: "content_block_delta"
        properties
            type: Literal["content_block_delta"]
            index: int
            delta: str

DONE ReasoningDeltaEvent -> ant: thinking_delta, oai: response.reasoning_text.delta
    oai: 
        object: response.reasoning_text.delta
        event_type: "response.reasoning_text.delta"

    properties:
        type: Literal["response.reasoning_text.delta"]
        item_id: str
        output_index: int # identifies the reasoning item/’/s position in response.output
        content_index: int
        delta: str
        sequence_number: int
    
    ant:
        object: RawContentBlockDeltaEvent
        event: "content_block_delta"
        properties:
            type: Literal["content_block_delta"] 
            index: int #identifies the content block’s position in message.content
            delta
                type: Literal["thinking_delta"]
                thinking: str
    


DONE ResponseStartedEvent -> ant: message_start, oai: response.created
    oai: ResponseCreatedEvent
    properties
        * response: Response
        * sequence_number: int
        * type 
    
    ant: RawMessageStartEvent
        properties
        * message: Message
        type
    

    


    
DONE TextDeltaEvent -> ant: text_delta, oai: response.output_text.delta
ProviderEvent -> all events that do not have a commonality, eg oai response.queued and multimedia response object parts, ant ping,
DONE ReasoningDeltaEvent -> ant: thinking_delta, oai: response.reasoning_text.delta
DONE ResponseCompletedEvent -> ant: message_stop, oai: response.incomplete                                                                                                                                                                               
DONE ToolArgumentsDeltaEvent -> ant: input_json_delta, oai: response.function_call_arguments.delta
ResponseFailedEvent -> ant: error, oai: error or response.failed
UsageUpdatedEvent -> ant: message_delta.usage, oai: response.completed.usage, response.incomplete.response.usage, response.failed.response.usage
AnnotatedAddedEvent -> 
ToolCallStartedEvent -> ant: content_block_start, content_block_type: tool_use, oai: response.output_item.added, output_item.type: fuction_call



class TextDeltaEvent(BaseModel):
    type: Literal["text.delta"] = "text.delta"

    delta: str

    provider: Literal["openai", "anthropic"]
    response_id: str | None = None

    output_index: int | None = None
    content_index: int | None = None
    item_id: str | None = None

    raw_event: object | None = None

    
resp = client.send()
streamed_resp = client.stream(
    provider="xyz"
)
stream():
    _resp = anthropic_stream_handler()
    if _resp.type == "message_start":
        TessaractCanonicalType(
            payload=_resp,
            _resp.type = "message_start"
        )

stream():
    openai_handler()
for evt in streamed_resp.output_text:
    print(evt)

for evt in streamed_resp.content_block:
    print(evt)




Anthropic Response Events

"top level streams"
message_start
content_block_start
content_block_delta
    - types
    text_delta
    input_json_delta
    citations_delta
    thinking_delta
    signature_delta

content_block_stop
message_delta
message_stop
ping
error

OpenAI Response Events
response lifecycle

response.queued
response.created
response.in_progress
response.completed
response.incomplete
response.failed
error

output item and content parts
response.output_item.added
response.output_item.done

response.content_part.added
response.content_part.done

text, refusal and annotations
response.output_text.delta
response.output_text.done
response.output_text.annotation.added

response.refusal.delta
response.refusal.done

function calls
response.function_call_arguments.delta
response.function_call_arguments.done

Reasoning events
response.reasoning_summary_part.added
response.reasoning_summary_part.done

response.reasoning_summary_text.delta
response.reasoning_summary_text.done

response.reasoning_text.delta
response.reasoning_text.done


'''