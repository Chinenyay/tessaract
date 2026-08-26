from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel

JSONSchema = Mapping[str, Any]

class FunctionTool(BaseModel):
    # tool definition
    name: str
    description: str
    input_schema: JSONSchema
    strict: bool | None = None


# function toolcall
# function tool definition
# function tool result

