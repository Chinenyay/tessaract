import os

from dotenv import load_dotenv

from tessaract.client import Tessaract
from tessaract.providers import OpenAIProvider
from tessaract.types.request import ReasoningOptions

load_dotenv()

client = Tessaract(
    {
        "oai": OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"])
    }
)

luna="oai/gpt-5.6-luna"

response = client.send(
    model=luna,
    input="what is 564 * 900",
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
        print(item.raw)

