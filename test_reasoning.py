import os
from dotenv import load_dotenv

from src.client import Tessaract
from src.providers import OpenAIProvider
from src.types.request import ReasoningOptions
from src.types.output_types import AssistantMessage, ReasoningOutputItem

load_dotenv()

client = Tessaract(
    {
        "oai": OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"])
    }
)

luna="oai/gpt-5.6-luna"

response = client.send(
    model=luna,
    input="Explain the Navier-Stokes problem and how to approach solving it.",
    reasoning=ReasoningOptions(
        effort="high",
        summary="detailed"
    )
)

for item in response.output:
    if item.type == "assistant_message":
        print("Answering...")
        for block in item.content:
            print(block.text)
    elif item.type == "reasoning":
        print("Thinking...")
        print(item.content or "")
        print(item.text or "")
