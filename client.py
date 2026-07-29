from rough.canonical_types import OpenAIProvider, AnthropicProvider
from adapters import openai_adapter
from rough.canonical_types import Response


SUPPORTED_PROVIDERS = OpenAIProvider | AnthropicProvider


class Tessaract:
    def __init__(self, providers: dict[str, object]):
        self.providers = providers

    def send(self, messages, model) -> Response | None:
        # {"openai": OpenAIProvider(...), "anthropic": (AnthropicProvider)}
        # set( ("openai", OpenAIProvider()), ("anthropic", AnthropicProvider))
        # _provider = set(provider.items())
        if len(self.providers) == 1:
            # _provider_adapter = self.providers.values()
            # if not isinstance(_provider_adapter, SUPPORTED_PROVIDERS):
            #     raise ValueError("provider not supported")

            model_parts = model.split("/")
            model_prefix = model_parts[0]
            model_name = model_parts[1]

            if model_prefix not in self.providers.keys():
                raise ValueError("provider prefix must match registered provider in tessaract object")

            _request_provider = self.providers[model_prefix]

            if isinstance(_request_provider, OpenAIProvider):

                _request = openai_adapter.OpenAIAdapter()
                _response = _request.generate_sync(
                    model=model_name,
                    input=messages
                )

                return _response
        else:
            pass

        

        

        




#     response2: Response = client.send(
#     provider="xyz"
#     messages=history
# )

