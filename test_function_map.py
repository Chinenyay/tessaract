from src.tools.function import FunctionTool, InputSchema, Property
# from src.types.input_types import ToolResult
from src.adapters.openai_adapter import OpenAIAdapter
from src.providers.openai_provider import OpenAIProvider

get_weather = FunctionTool(
    name="get_weather",
    description="get the weather of a city",
    input_schema=InputSchema(
        properties={
            "city": Property(
                type="string",
                description="the city to find weather for, eg Paris."
            )
        }
    )
)

tool_list = [get_weather]

api_key="xyz123..."

# tool_result = ToolResult(
#     call_id="xyz..",
#     result="hello world"
# )

openai_provider = OpenAIProvider(api_key=api_key)

native_schema = OpenAIAdapter(provider=openai_provider).map_function_schema(tool_list)

print(native_schema)