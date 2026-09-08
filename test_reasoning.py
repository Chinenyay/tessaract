import os
from dotenv import load_dotenv

from src.client import Tessaract
from src.providers import OpenAIProvider
from src.types.request import ReasoningOptions

load_dotenv()

client = Tessaract(
    {
        "oai": OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"])
    }
)

luna="oai/gpt-5.6-luna"

response = client.send(
    model=luna,
    input="How would you solve the unified field theory?",
    reasoning=ReasoningOptions(
        effort="high",
        summary="detailed"
    )
)

print(response.output)
