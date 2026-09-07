import os

from dotenv import load_dotenv
import json

from src.client import Tessaract
from src.providers.openai_provider import OpenAIProvider
from src.tools.function import FunctionTool, InputSchema, Property
from src.types.input_types import UserMessage, ToolResult
from src.types.request import ReasoningOptions

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

weather_tool = FunctionTool(
    name="get_weather",
    description="get the weather of a city",
    input_schema=InputSchema(
        properties={
            "city": Property(
                description="the city to provide weather for, eg Paris, London.",
                type="string"
            ),
        },
        required=["city"],
        additionalProperties=False
    ),
    strict=True
)

TOOLS = [weather_tool]

TOOL_MAP = {"get_weather": get_weather}

def run_agent_turn(history: list, input):
    model="oai/gpt-5.6-luna"

    response = client.send(
        model=model,
        input=history,
        tools=TOOLS,
        reasoning=ReasoningOptions(
            effort="high",
            summary="detailed"
        )
    )

    history.extend(response.output)

    for item in response.output:
        if item.type == "tool_call":
            tool_name = item.name
            tool_args = json.loads(item.arguments)

            print(f"{model} is requesting tool: {tool_name}")
            function = TOOL_MAP[tool_name]

            result = function(**tool_args)

            result_schema = ToolResult(
                call_id = item.call_id,
                result=result
            )

            history.append(result_schema)

            response = client.send(
                model=model,
                input=history,
                tools=TOOLS,
                reasoning=ReasoningOptions(
                    effort="high",
                    summary="detailed"
                )
            )

    # print(f"\n Thinking... {response.reasoning}")

    # print(f"\n Answering... {response.output_text}\n")
            print(response.output)

def main():
    print("Hello, this is your assistant. Type your message here...")

    history = []

    while True:
        _input = input("\nYou:")

        if _input == "exit()":
            break

        history.append(_input)

        run_agent_turn(history=history, input=_input)

if __name__ == "__main__":
    main()