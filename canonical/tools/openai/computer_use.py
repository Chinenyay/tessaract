from typing import Literal

from pydantic import BaseModel

from ..base import ClientExecutedProviderTool


class OpenAIClick(BaseModel):
    type: Literal["click"] = "click"
    button: Literal["left", "right", "wheel", "back", "forward"]
    x: int
    y: int
    keys: list[str] | None = None

class OpenAIType(BaseModel):
    type: Literal["type"] = "type"
    text: str

class OpenAIKeypress(BaseModel):
    type: Literal["keypress"] = "keypress"
    keys: list["str"]

class OpenAIMove(BaseModel):
    type: Literal["move"] = "move"
    x: int
    y: int
    keys: list[str] | None = None

class OpenAIDoubleClick(BaseModel):
    type: Literal["double_click"] = "double_click"
    keys: list[str] | None
    x: int
    y: int

class OpenAIDrag(BaseModel):
    type: Literal["drag"] = "drag"
    keys: list[str] | None

class OpenAIScreenshot(BaseModel):
    type: Literal["screenshot"]

class OpenAIScroll(BaseModel):
    type: Literal["scroll"] = "scroll"
    scroll_x: int
    scroll_y: int
    x: int
    y: int
    keys: list[str] | None = None
    
class OpenAIWait(BaseModel):
    type: Literal["wait"] = "wait"

type OpenAIComputerAction = (
    OpenAIClick
    | OpenAIDoubleClick
    | OpenAIDrag
    | OpenAIKeypress
    | OpenAIMove
    | OpenAIScreenshot
    | OpenAIScroll
    | OpenAIType
    | OpenAIWait
)

class SafetyCheck:
    id: str
    code: str | None = None
    message: str | None = None

class Agent:
    agent_name: str

class OpenAIComputerUseToolCall(ClientExecutedProviderTool):
    type: Literal["computer"] = "computer"
    id: str
    action: OpenAIComputerAction | None = None
    actions: list[OpenAIComputerAction] | None = None
    status: Literal[
        "in_progress",
        "completed",
        "incomplete"
    ]
    pending_safety_checks: list[SafetyCheck]
    agent: Agent | None

class OpenAIComputerScreenshot(BaseModel):
    type: Literal["computer_screenshot"] = "computer_screenshot"
    file_id: str | None = None
    image_url: str | None = None

class OpenAIComputerUseToolResult:
    type: Literal["computer_call_output"] = "computer_call_output"
    call_id: str
    output: OpenAIComputerScreenshot
    acknowledged_safety_checks: list[SafetyCheck] | None
