from collections.abc import Mapping
from typing import Any

from canonical.input_types import ContentPart

from .base import ClientTool

type JSONSchema = Mapping[str, Any]

class FunctionTool(ContentPart, ClientTool):
    name: str
    description: str
    input_schema: JSONSchema

