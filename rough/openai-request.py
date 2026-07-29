import os
import json
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from openai import OpenAI
from openai.types.responses import Response

load_dotenv()

INPUT_HISTORY_PATH = Path("openai_input_history.json")
INITIAL_HISTORY = [
    {
        "role": "developer",
        "content": (
            '''
            You are a fortune teller. 
            Use the sample_tool to answer the user's horoscope related questions."
            '''.strip()
        ),
    }
]


def serialize_for_json(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    if hasattr(obj, "to_dict"):
        return obj.to_dict()

    raise TypeError(
        f"Object of type {obj.__class__.__name__} is not JSON serializable"
    )


def save_input_history(history, path=INPUT_HISTORY_PATH):
    """Persist the current API input history without leaving a partial file."""
    path = Path(path)
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")

    with temporary_path.open("w", encoding="utf-8") as history_file:
        json.dump(
            history,
            history_file,
            indent=2,
            default=serialize_for_json,
        )

    temporary_path.replace(path)


def load_input_history(path=INPUT_HISTORY_PATH):
    """Load a previous history, or start a new one if none has been saved."""
    path = Path(path)
    if not path.exists():
        return [item.copy() for item in INITIAL_HISTORY]

    with path.open(encoding="utf-8") as history_file:
        history = json.load(history_file)

    if not isinstance(history, list):
        raise ValueError(f"{path} must contain a JSON list")

    return history


class OpenAIRequest:
    '''
    Make a request to the OpenAI API
    '''
    def __init__(self, openai_api_key: str, model: str, input: str | list, tools: Optional[list], **kwargs):
        self.client = OpenAI()
        self.openai_api_key = openai_api_key
        self.model = model
        self.input = input
        self.tools = tools
        self.__dict__.update(kwargs)


    def response(self) -> Response:
        _response = self.client.responses.create(
            model=self.model,
            input=self.input,
            tools=self.tools
        )
        return _response
    
    def save_response(self, path) -> str:
        _response = self.response()
        with open(path, "w") as f:
            json.dump(_response.model_dump(), f, indent=2)
        print(f'saved to {path}')
        return path

def sample_tool(arg):
    return f"{arg}: Next Tuesday you will befriend a baby otter."


tools = [
    {
        "type": "function",
        "name": "sample_tool",
        "description": "Get today's horoscope for an astrological sign.",
        "parameters": {
            "type": "object",
            "properties": {
                "arg": {
                    "type": "string",
                    "description": "An astrological sign like Taurus or Aquarius",
                },
            },
            "required": ["arg"],
        },
    },
]

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def multiturn(history, user_input, history_path=INPUT_HISTORY_PATH):
    history.append({"role": "user", "content": user_input})
    # Save immediately so the user's input survives an API or network error.
    save_input_history(history, history_path)

    while True:
        req = OpenAIRequest(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-5.4",
            input=history,
            tools=tools
        )

        resp = req.response()

        history += resp.output
        save_input_history(history, history_path)

        function_calls = [item for item in resp.output if item.type == "function_call" and item.name == "sample_tool"]

        if len(function_calls) == 0:
            print(f"\nAssistant: {resp.output_text}")
            return

        for function_call in function_calls:
            args = json.loads(function_call.arguments)["arg"]
            result = sample_tool(args)

            history.append({
                "type": "function_call_output",
                "call_id": function_call.call_id,
                "output": result
            })
            save_input_history(history, history_path)

def take_input(history_path=INPUT_HISTORY_PATH):
    input_list = load_input_history(history_path)
    print("add a new message:")

    while True:
        user_input = input("You:\n")
        if user_input == "exit()":
            break
        multiturn(
            history=input_list,
            user_input=user_input,
            history_path=history_path,
        )

    return input_list


def main():
    take_input()


if __name__ == "__main__":
    main()
