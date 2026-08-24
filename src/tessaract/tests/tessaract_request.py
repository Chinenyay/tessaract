import os
from dotenv import load_dotenv

from ..client import Tessaract
from ..providers import OpenAIProvider

from ..request import Input

from ..input_types import Text, UserMessage


load_dotenv()

client = Tessaract(
    {
        "oai": OpenAIProvider(
            api_key=os.environ["OPENAI_API_KEY"]
        )
    }
)

history = [
        UserMessage(
            content="How are you?"
            )
        ]

response = client.send(
    model="oai/gpt-5.5",
    input=history
)

# history.append(response.output)

# history = [
#         UserMessage(
#             content="whats up?"
#             )
#         ]


output=response.output
output_list = []
for item in output:
    output_list.append(item.raw)

print(output_list)