from .providers import OpenAIProvider
from .adapters import OpenAIAdapter
from .types import Request

class Tessaract:
    def __init__(self, providers: dict[str, OpenAIProvider]):
        self.providers = providers
        self.adapters: dict[str, OpenAIAdapter ] = {} # value should be a union of OpenAIAdapter | AnthropicAdapter once implemented
        self.register_adapter()

    def register_adapter(self):
        for prefix, provider in self.providers.items():
            if isinstance(provider, OpenAIProvider):
                adapter = OpenAIAdapter(provider)
            else:
                raise NotImplementedError("not yet implemented")
            self.adapters[prefix] = adapter

    def _normalize_model_name(self, model: str):
        model_parts = model.split("/")
        model_prefix = model_parts[0]
        model_name = model_parts[1]

        return (model_prefix, model_name)

   def send(
            self, model: str, 
            input: list[str | UserMessage | AssistantMessage],
            reasoning: ReasoningOptions | None = None,
            tools: list[FunctionTool] | None = None
        ) -> Response | None:

        model_prefix, model_name = self._normalize_model_name(model=model)

        if model_prefix not in self.providers:
            raise ValueError("provider prefix must match registered provider in tessaract object")

        _request_provider = self.providers[model_prefix]

        _tools = tools if tools is not None else []

        _tessaract_request = self._build_request_model(model=model_name, input=input, reasoning=reasoning, tools=_tools)

        _api_key = _request_provider.api_key

        if _api_key is None:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        
        if isinstance(_request_provider, OpenAIProvider):

            adapter = self.adapters[model_prefix]

            _response = adapter.generate_sync(request=_tessaract_request)
            return cast(Response, _response)

        return None