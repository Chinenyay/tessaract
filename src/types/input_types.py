from typing import Any, Literal

from pydantic import BaseModel

from ..adapters.adapter import Adapter


class InputType(BaseModel):
    def raw(self, adapter: Adapter) -> Any:
        ...

class UserMessage(InputType):
    role: Literal["user"] = "user"
    content: str | list[dict]

    def raw(self, adapter: Adapter):
        return adapter.map_input_message(self)
