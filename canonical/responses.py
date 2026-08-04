from dataclasses import dataclass
class Response:
    def __init__(self, raw_payload):
        self.raw_payload = raw_payload
    
    @property
    def payload(self):
        return self.raw_payload
@dataclass
class UsageBase:
    input_tokens: int
    cached_tokens: int | list
    cache_write_tokens: int
    output_tokens: int
    reasoning_tokens: int
    tessaract_computed_total_tokens: int | None = None
    provider_reported_total_tokens: int | None = None 

class OpenAIUsage(UsageBase):
    cached_tokens: int

class AnthropicUsage(UsageBase):
    cached_tokens: list[int]

type Usage = OpenAIUsage | AnthropicUsage # type alias for usage return type to do if isinstance(usage, AnthropicUsage) return AnthropicUsage

@dataclass
class GenerationParams:
    log_probs: list | None = None
    temperature: float | None = None
    top_p: float | None = None
    top_logprobs: int | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None


class OpenAIResponse(Response):
    def __init__(self, raw_payload):
            super().__init__(raw_payload)
            self._payload_object = raw_payload
            self._raw_payload = self._payload_object.model_dump(mode="python")

    @property
    def raw_object(self):
        return self._payload_object

    @property
    def raw_payload(self):
        return self._raw_payload
    
    @property
    def output_text(self):
        '''Returns final output text of the payload'''
        return self._payload_object.output_text

    @property
    def model(self):
        '''Model used to generate the response'''
        return self.raw_payload["model"]

    @property
    def response_id(self):
        return self.raw_payload["id"]

    @property
    def message_id(self) -> str | None:
        for item in self._payload_object.output:
            if item.type == "mesage":
                return item.id

        return None

    # returning multiple message ids, what would be the benefit?
    #     @property
    # def message_ids(self) -> list[str]:
    #     return [
    #         item.id
    #         for item in self._payload_object.output
    #         if item.type == "message"
    #     ]
    
    @property
    def previous_response_id(self):
        '''Returns None or the previous response id.'''
        return self._payload_object["previous_response_id"]

    @property
    def output_block(self):
        '''Returns all the content in the output block.'''
        return self.raw_payload["output"]
    
    @property
    def available_tools(self):
        '''Tools the model has chosen to call'''
        return self._payload_object.tools

    @property
    def tool_calls(self):
        return [
            item for item in self._payload_object.output
            if item.type in {
                "function_call",
                "custom_tool_call",
            }
        ]

    @property
    def time_data(self):
        pass

    @property
    def reasoning_config(self):
        return self._payload_object.reasoning
    
    @property
    def reasoning_block(self) -> list[object]:
        return [
            item for item in self._payload_object.output
            if item.type == "reasoning"
        ]
    
    @property
    def generation_parameters(self):
        p = self._payload_object

        return GenerationParams(
            log_probs=p.temperature,
            temperature=p.temperature,
            top_p=p.top_p,
            top_logprobs=p.top_logprobs,
            frequency_penalty=p.frequency_penalty,
            presence_penalty=p.presence_penalty
        )

    @property
    def output_logprobs(self) -> list[object]:
        results = []

        for item in self._payload_object.output:
            if item.type != "message":
                continue

            for content in item.content:
                if content.type == "output_text":
                    results.extend(content.logprobs or [])

        return results

    @property
    def prompt_cache_key(self):
        return self._payload_object.prompt_cache_key

    @property
    def token_usage(self) -> OpenAIUsage | None:
        '''Number of tokens used by this response'''
        usage = self._payload_object.usage

        if usage is None:
            return None

        return OpenAIUsage(
            input_tokens=usage.input_tokens,
            cached_tokens=usage.cached_tokens,
            cache_write_tokens=usage.cache_write_tokens,
            output_tokens=usage.output_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            provider_reported_total_tokens=usage.provider_reported_total_tokens
        )

    @property
    def status(self) -> str | None:
        return self._payload_object.status

    @property
    def is_complete(self) -> bool:
        return self.status == "completed"

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            "completed",
            "failed",
            "cancelled",
            "incomplete",
        }
    
    @property
    def provider_metadata(self):
        # p = self._payload_object
        # time_created = p["created_at"]
        # time_completed = p["completed_at"]

        # metadata = p["metadata"]
        # service_tier = p["service_tier"]
        # billing_payer = p["billing"]["payer"]
        # user = p["user"]

        # return OpenAIMetadata(
        #     time_created=time_created,
        #     time_completed=time_completed,
        #     metadata=metadata,
        #     service_tier=service_tier,
        #     billing_payer=billing_payer,
        #     user=user
        # )
    
    @property
    def safety_moderation_metadata(self):
        # p = self._payload_object        
        # moderation = p["moderation"]
        # safety_identifier = p["safety_identifier"]

        # return (
        #     moderation,
        #     safety_identifier
        # )

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
    def available_tools(self):
        '''Tools the model has chosen to call'''
        return self._payload_object.tools

    @property
    def tool_calls(self):
        return [
            item for item in self._payload_object.output
            if item.type in {
                "function_call",
                "custom_tool_call",
            }
        ]

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

class Stream:
    pass