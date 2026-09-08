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
    input="How would you solve the unified field theory?",
    reasoning=ReasoningOptions(
        effort="high",
        summary="detailed"
    )
)

for item in response.output:
    if isinstance(item, AssistantMessage):
        print("Answering...")
        for block in item.content:
            print(block.text)
    elif isinstance(item, ReasoningOutputItem):
        print("Thinking...")
        print(item.content or "")
        print(item.text or "")
