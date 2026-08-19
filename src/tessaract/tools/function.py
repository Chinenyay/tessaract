from collections.abc import Mapping
from typing import Any

JSONSchema = Mapping[str, Any]

class FunctionTool:
    # tool definition
    name: str
    description: str
    input_schema: JSONSchema


# function toolcall
# function tool definition
# function tool result

