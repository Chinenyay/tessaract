from typing import Optional
from openai import OpenAI
from rough.canonical_types import OpenAIProvider, GatewayError, OpenAIResponse

class OpenAIAdapter:
    def __init__(self):
        self._client_args = OpenAIProvider()
        self._client = OpenAI(*self._client_args.model_dump(exclude_unset=True, exclude_none=True))

    def generate_sync(self, model, input, instructions: Optional[str] = None):

        try:
            response = self._client.responses.create(
                model=model,
                input=input,
                instructions=None
            )

            tessaract_response = OpenAIResponse(response)

            return tessaract_response
        
        except Exception:
            raise GatewayError("failed to generate a response.")


if __name__ == '__main__':
    pass