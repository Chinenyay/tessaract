from typing import Optional
from openai import OpenAI
from canonical_types.canonical_types import OpenAIProvider, GatewayError, OpenAIResponse

class OpenAIAdapter:
    def __init__(self):
        self._client_args = OpenAIProvider()
        self._client = OpenAI(*self._client_args)

    def generate_sync(self, model, input, instructions: Optional[str]):

        try:
            response = self._client.responses.create(
                model=model,
                input=input,
                instructions=instructions
            )

            tessaract_response = OpenAIResponse(response)

            return tessaract_response
        
        except Exception:
            raise GatewayError("failed to generate a response.")


if __name__ == '__main__':
    pass