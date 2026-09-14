from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Property(BaseModel):
    type: Literal["string", "number", "integer", "boolean", "array", "null"]
    description: str

class InputSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    type: Literal["object"] = "object"
    properties: dict[str, Property] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)
    additionalProperties: bool | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode="after")
    def _model_validator(self):
        invalid = set(self.required) - set(self.properties)

        if invalid:
            raise ValueError(
                f"required contains undefined properties: {invalid}"
            )

        return self

class FunctionTool(BaseModel):
    name: str
    description: str
    input_schema: InputSchema | None = None
    strict: bool | None = None
    provider_options: dict[str, Any] = Field(default_factory=dict)