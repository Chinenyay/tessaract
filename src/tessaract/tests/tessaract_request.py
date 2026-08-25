import os
from dotenv import load_dotenv

from ..client import Tessaract
from ..providers import OpenAIProvider

from ..request import Input

from ..input_types import Text, UserMessage
from ..tools.function import FunctionTool


load_dotenv()

client = Tessaract(
    {
        "oai": OpenAIProvider(
            api_key=os.environ["OPENAI_API_KEY"]
        )
    }
)

def get_weather(city: str):
    normalize_city = city.lower()
    fake_dict = {"paris": "sunny 19C", "amsterdam": "rainy 14C"}

    return fake_dict.get(normalize_city, f"Unable to find weather for {city}")

TOOL_MAP = {"get_weather": get_weather}

TOOLS = [
    FunctionTool(
        name="get_weather",
        description="get the weather of a city",
        input_schema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "the city, eg paris",
                },
            "required": ["city"],
            }
        }
    )
]

history = [
        UserMessage(
            content="What is the capital of France?"
            )
        ]


response = client.send(
    model="oai/gpt-5.5",
    input=history
)

print(response.output_text)

history.append(response.output)

history.append(
    UserMessage(content="What is the weather there?")
)

response_2 = client.send(
    model="oai/gpt-5.5",
    input=history
)

response_2_output = response_2.output

for item in response_2_output:
    if item.type == ""



print(response_2.output)

