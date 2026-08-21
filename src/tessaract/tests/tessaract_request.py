import os
from dotenv import load_dotenv

from ..client import Tessaract
from ..providers import OpenAIProvider

from ..request import Input

from ..input_types import Text, UserMessage


load_dotenv()

# client = Tessaract(
#     {
#         "oai": OpenAIProvider(
#             api_key=os.environ["OPENAI_API_KEY"]
#         )
#     }
# )

response = client.send(
    model="oai/gpt-5.5",
    input=[
        UserMessage(
            content="How are you?"
            )
        ]
)

print(response)