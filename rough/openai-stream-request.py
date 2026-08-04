import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def request():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


    stream = client.responses.create(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "user",
                "content": "Say 'double bubble bath' ten times fast.",
            },
        ],
        stream=True
    )

    collated_response = []

    for evt in stream:
        collated_response.append(evt.to_dict())


    print(collated_response)
    return collated_response

payload = request()

with open("openai-stream-payload.txt", "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)



