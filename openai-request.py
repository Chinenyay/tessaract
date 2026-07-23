import os
import json
from dotenv import load_dotenv

from openai import OpenAI
from openai.types.responses import Response

load_dotenv()
class OpenAIRequest:
    '''
    Make a request to the OpenAI API
    '''
    def __init__(self, openai_api_key: str, model: str, input: str | list, **kwargs):
        self.client = OpenAI()
        self.openai_api_key = openai_api_key
        self.model = model
        self.input = input
        self.__dict__.update(kwargs)


    def response(self) -> Response:
        _response = self.client.responses.create(
            model=self.model,
            input=self.input
        )
        return _response
    
    def save_response(self, path) -> str:
        _response = self.response()
        with open(path, "w") as f:
            json.dump(_response.model_dump(), f, indent=2)
        print(f'saved to {path}')
        return path

def main():
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
    req = OpenAIRequest(
        openai_api_key=OPENAI_API_KEY,
        model="gpt-5.4",
        input="How are you?"
    )
    print(req.save_response(path="test.txt"))
if __name__ == "__main__":
    main()
    
