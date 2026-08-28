from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

JSONSchema = Mapping[str, Any]

class FunctionTool(BaseModel):
    name: str
    description: str
    input_schema: JSONSchema
    strict: bool | None = None
    # add a payload for non-common fields, like anthropic tool_examples

class Property(BaseModel):
    name: str
    type: Literal["string", "number", "integer", "boolean", "array", "null"]
    description: str

class InputSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    type: Literal["object"] = "object"
    properties: dict[str, Property] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)
    additionalProperties: bool | None = None

    @model_validator(mode="after")
    def _model_validator(self):
        invalid = set(self.required) - set(self.properties)

        if invalid:
            raise ValueError(
                f"required contains undefined properties: {invalid}"
            )

        return self