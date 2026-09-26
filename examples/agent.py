"""A reasoning + tool-calling agent built on Tessaract and the OpenAI API.

Run:
    export OPENAI_API_KEY=sk-...
    uv run python examples/agent.py
"""

import json
import os
from datetime import datetime, timezone

from tessaract import (
    FunctionTool,
    FunctionToolResult,
    InputSchema,
    OpenAIProvider,
    Property,
    ReasoningOptions,
    Tessaract,
    UserMessage,
)

MODEL = os.environ.get("TESSARACT_MODEL", "oai/gpt-5.6-luna")
INSTRUCTIONS = "You are a helpful assistant. Use tools when they help; be concise."
MAX_STEPS = 10


# --- Tools -----------------------------------------------------------------

def get_time() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_weather(city: str) -> str:
    temps = {"paris": "19C", "amsterdam": "20C", "lagos": "31C"}
    temp = temps.get(city.lower())
    if temp is None:
        return json.dumps({"error": f"No weather data for {city!r}"})
    return json.dumps({"city": city, "temperature": temp})


FUNCTIONS = {"get_time": get_time, "get_weather": get_weather}

TOOLS = [
    FunctionTool(
        name="get_time",
        description="Get the current UTC time as an ISO-8601 string.",
        strict=False,
    ),
    FunctionTool(
        name="get_weather",
        description="Get the current temperature for a city.",
        input_schema=InputSchema(
            properties={
                "city": Property(type="string", description="City name, e.g. Paris."),
            },
            required=["city"],
            additionalProperties=False,
        ),
        strict=True,
    ),
]

REASONING = ReasoningOptions(effort="medium", summary="auto")


# --- Agent -----------------------------------------------------------------

client = Tessaract(
    providers={"oai": OpenAIProvider()}  # reads OPENAI_API_KEY
)


def execute(call) -> FunctionToolResult:
    """Run one function call and wrap its output (or error) for the model."""
    fn = FUNCTIONS.get(call.name)
    if fn is None:
        return FunctionToolResult(call_id=call.call_id, result=f"Unknown tool {call.name!r}", is_error=True)
    try:
        result = fn(**call.arguments)
    except Exception as exc:
        return FunctionToolResult(call_id=call.call_id, result=str(exc), is_error=True)
    return FunctionToolResult(call_id=call.call_id, result=result)


def run_turn(history: list, user_text: str) -> str:
    history.append(UserMessage(content=user_text))

    for _ in range(MAX_STEPS):
        response = client.send(
            model=MODEL,
            input=history,
            tools=TOOLS,
            reasoning=REASONING,
            request_options={"instructions": INSTRUCTIONS},
        )

        history.extend(response.output)

        for item in response.output:
            if item.type == "reasoning" and item.text:
                print(f"  [thinking] {item.text}")

        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            return response.output_text

        for call in calls:
            print(f"  [tool] {call.name}({call.arguments})")
            history.append(execute(call))

    return "Stopped: too many tool-calling steps."


def main() -> None:
    history: list = []
    print("Type 'q' to quit.")
    while True:
        user_text = input("\nyou > ").strip()
        if user_text.lower() in {"q", "quit", "exit"}:
            break
        if user_text:
            print(f"agent > {run_turn(history, user_text)}")


if __name__ == "__main__":
    main()
