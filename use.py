import os

from dotenv import load_dotenv

from src.client import Tessaract
from src.providers.openai_provider import OpenAIProvider

load_dotenv()
client = Tessaract(
    {
        "oai": OpenAIProvider(
            api_key=os.environ["OPENAI_API_KEY"]
        )
    }
)

# make a single turn request
response = client.send(
    model="oai/gpt-5.6-luna",
    input="What is the capital of France?"
)

print(response.output_text)