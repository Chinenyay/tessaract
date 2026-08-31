import os
from dotenv import load_dotenv
import json

from ..client import Tessaract
from ..providers import OpenAIProvider

from ..request import Input, ReasoningOptions

from ..input_types import Text, UserMessage, ToolCallResult
from ..tools.function import FunctionTool, InputSchema, Property


load_dotenv()

client = Tessaract(
    {
        "oai": OpenAIProvider(
            api_key=os.environ["OPENAI_API_KEY"]
        )
    }
)

def get_weather(city: str):
    normalize_city = city.lower()
    fake_dict = {"paris": "sunny 19C", "amsterdam": "rainy 14C"}

    return fake_dict.get(normalize_city, f"Unable to find weather for {city}")

TOOL_MAP = {"get_weather": get_weather}

# {
# 	"type": "function",
# 	"name": "get_weather",
# 	"description": "some description",
# 	"parameters": {
# 		"type": "object",
# 		"properties": {
# 			"city": {
# 				"type": "string",
# 				"description": "some description",
# 			},
# 		},
# 		"required": [sign],
# 	},
# }

# TOOLS = [
#     FunctionTool(
#         name="get_weather",
#         description="get the weather of a city",
#         input_schema=InputSchema(
#             properties={
#                 "city": Property(
#                     type="string",
#                     description="the city to get weather about"
#                 )
#             },
#             required=["city"],
#             additionalProperties=False
#         ),
#         strict=True
#     )
# ]

history = [
        UserMessage(
            content="How would you prove the Reimann hypothesis?"
            )
        ]


response = client.send(
    model="oai/gpt-5.6-luna",
    input=history,
    reasoning=ReasoningOptions(
        summary="auto"

    )
)

print(response.raw_response)

# history.append(response.message)

# history.append(
#     UserMessage(content="What is the weather there?")
# )

# response_2 = client.send(
#     model="oai/gpt-5.5",
#     reasoning="high",
#     input=history,
#     tools=TOOLS
# )

# history.append(response_2.message)

# print(response_2.raw_response)

# response_2_output = response_2.output

# for item in response_2_output:
#     if item.type == "tool_call":
#         tool_name = item.name
#         tool_args = json.loads(item.arguments)

#         function = TOOL_MAP[tool_name]

#         function_result = function(**tool_args)

#         history.append(
#             ToolCallResult(
#                 call_id=item.call_id,
#                 result=function_result
#             )
#         )

# response_3 = client.send(
#     model="oai/gpt-5.5",
#     input=history,
#     tools=TOOLS
# )



# print(response_3.output_text)

