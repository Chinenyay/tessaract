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
            content="Who was Cleopatra"
            )
        ]


response = client.send(
    model="oai/gpt-5.5",
    input=history
)

print(response.output_text)

history.append(response.output)
history.append(
    UserMessage(content="how old was she when she died?")
)

response_2 = client.send(
    model="oai/gpt-5.5",
    input=history

)

print(response_2.output_text)

# history = [
#         UserMessage(
#             content="whats up?"
#             )
#         ]

