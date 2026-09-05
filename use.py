import os

from dotenv import load_dotenv

from src.client import Tessaract
from src.providers.openai_provider import OpenAIProvider
from src.types.input_types import UserMessage

load_dotenv()
client = Tessaract(
    {
        "oai": OpenAIProvider(
            api_key=os.environ["OPENAI_API_KEY"]
        )
    }
)



def run_agent_turn(history: list, input):

    history.append(input)

    model="oai/gpt-5.6-luna"

    response = client.send(
        model=model,
        input=history
    )

    history.append(response.output)

    print(f"\n{response.output_text}\n")

def main():
    print("Hello, this is your assistant. Type your message here...")

    history = []


    while True:
        _input = input("\nYou:")

        if _input == "exit()":
            break
        
        history.append(_input)
        run_agent_turn(history=history, input=_input)

main()