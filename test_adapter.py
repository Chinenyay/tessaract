from src.providers.openai_provider import OpenAIProvider
from src.adapters.openai_adapter import OpenAIAdapter
from src.types.input_types import UserMessage


provider = OpenAIProvider(api_key="sk...")
adapter = OpenAIAdapter(provider=provider)


history = [
    UserMessage(
    content="hello"
),
UserMessage(
    content="hello"
)
]

data = message.raw(adapter)
print(data)