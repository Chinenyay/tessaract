import os
from dotenv import load_dotenv
from tessaract.tessaract import Tessaract, OpenAIProvider

load_dotenv()

client = Tessaract(
    {
        "oai": OpenAIProvider(
            api_key=os.environ["OPENAI_API_KEY"],
        )
    }
)

response = client.send(
    model="oai/gpt-5.5",
    messages=[{"role": "user", "content": "How are you?"}]
)



