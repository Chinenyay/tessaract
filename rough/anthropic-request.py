import json
import os

import anthropic
from dotenv import load_dotenv
from anthropic.types.message import Message

load_dotenv()

class AnthropicRequest:
    def __init__(self, **kwargs):
        self.client = anthropic.Anthropic()
        self.__dict__.update(kwargs)
    
    def response(self) -> Message:
        _response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=self.messages
        )

        return _response

def main():
    ANT_API_KEY=os.environ["ANTHROPIC_API_KEY"]
    req = AnthropicRequest(
        api_key=ANT_API_KEY,
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": "How are you?"
            }
        ],
    )
    with open("anthropic_response_payload.text", "w") as f:
        data = json.dumps(req.response().model_dump(), indent=2)
        f.write(data)
        


if __name__ == "__main__":
    main()
    
