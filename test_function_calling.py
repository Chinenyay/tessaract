import os
from typing import Any
from dotenv import load_dotenv

import json

from src.client import Tessaract
from src.providers import OpenAIProvider
from src.tools.function import FunctionTool, InputSchema, Property
from src.types.response import Response
from src.types.input_types import UserMessage, FunctionToolResult

load_dotenv()

client = Tessaract({
    "oai": OpenAIProvider(
        api_key=os.environ["OPENAI_API_KEY"]
    )
})

def _get_weather(city: str):
    normalize_city = city.lower()
    fake_dict = {"paris": "sunny 19C", "amsterdam": "rainy 14C"}

    return fake_dict.get(normalize_city, f"Unable to find weather for {city}")

get_weather = "get_weather"

get_weather_schema = FunctionTool(
    name=get_weather,
    description="get weather for a city",
    input_schema=InputSchema(
        properties={
            "city": Property(
                type="string",
                description="the city to get weather for. eg paris."
            )
        },
        required=["city"],
        additionalProperties=False
    ),
)

TOOLS = [get_weather_schema]

TOOL_MAP = {get_weather: _get_weather}

model ="oai/gpt-5.6-luna"

history: list[Any] = [
    UserMessage(
        content="what is the weather in Paris?"
    )
]

response_1 = client.send(
    model=model,
    tools=TOOLS,
    input=history,
)

history.extend(response_1.output)

for item in response_1.output:
    if item.type == "function_call":
        name = item.name
        args = json.loads(item.arguments)

        print(f"{model} is request tool: {name} with args: {args}")

        handler = TOOL_MAP[name]

        result = handler(**args)

        history.append(
            FunctionToolResult(
                call_id=item.call_id,
                result=result
            )
        )
    elif item.type == "reasoning":
        print(item.content)
        print(item.text)

    elif item.type == "assistant_message":
        
        print(response_1.output_text)


response_2 = client.send(
    model=model,
    input=history,
    tools=TOOLS
)
for item in response_2.output:
    if item.type == "assistant_message":
        print(item.raw)
    if item.type == "reasoning":
        print(item.raw)
print(response_2.output_text)




