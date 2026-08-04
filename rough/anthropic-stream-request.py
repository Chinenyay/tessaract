import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

def request():
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


    stream = client.messages.stream(
        max_tokens=1024,
        model="claude-opus-5",
        messages=[
            {
                "role": "user",
                "content": "Say 'double bubble bath' ten times fast.",
            },
        ]
    )

    collated_response = []

    with stream as s:
        for evt in s:
            collated_response.append(evt.to_dict())

    return collated_response

payload = request()

with open("anthropic-stream-with-object.txt", "w", encoding="utf-8") as f:
    for evt in payload:
        f.write(str(evt))
        f.write("\n")




