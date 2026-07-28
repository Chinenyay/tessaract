from dataclasses import dataclass

@dataclass
class Message:
    pass 

@dataclass
class UserMessage(Message):
    text: str

@dataclass
class SystemMessage(Message):
    text: str 

@dataclass
class ToolCallResult(Message):
    tool_call_id: str
    results: str


class Response(Message):
    raw_data = None
    def __init__(self):
        pass

    @property
    def type(self):
        return "text"
    
class TextResponse(Response):

    @property
    def text(self):

        return "Hello from GPT"

    @property
    def type(self):
        return "text"

class ToolCallResponse(Response):

    def __init__(self, tool_call_id: str):
        super().__init__()
        self.tool_call_id = tool_call_id

    @property
    def type(self):
        return "tool_call"



class Gateway():
    def __init__(self, model_name: str, provider: str):
        pass 

    def send(self, provider: str, messages: list[Message], temperature: float = 1) -> Response:

        return Response()
        

client = Gateway(model_name="gpt-5.6-sol", provider="openai")

history = [
    SystemMessage("You are a mathematician"),
    UserMessage("What is the square root of 64")
]

response1: Response = client.send(
    provider="xyz",
    messages=history
)

print(response1.type) # text_response

if isinstance(response1, TextResponse):
    print(response1.text)

history.append(response1)
history.append(UserMessage("Visit wikikpedia"))

response2: Response = client.send(
    provider="xyz"
    messages=history
)


if isinstance(response2, ToolCallResponse):
    # execute tool call

    result = ToolCallResult(
        tool_call_id=response2.tool_call_id,
        results="content of wikipedia"
    )

    history.append(result)    

response3 = client.send(
    messages=history
)

if isinstance(response3, TextResponse):

    print(response3.text)

