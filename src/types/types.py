from typing import Any

from pydantic import BaseModel


class OutputItem(BaseModel):
    raw: Any
