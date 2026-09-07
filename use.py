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
    return {city: "sunny 19C"}

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

    history.append(input)

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

    history.append(response.output)

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

        else:
            print(f"\n Thinking... {response.reasoning}")

            print(f"\n Answering... {response.output_text}\n")
    # print(response.raw_response)

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