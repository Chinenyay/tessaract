from typing import Literal

from pydantic import BaseModel


class Click:
    type: Literal["click"] = "click"
    button: Literal["left", "right", "wheel", "back", "forward"]
    x: int
    y: int
    keys: list[str] | None = None

class Type:
    type: Literal["type"] = "type"
    text: str

class Keypress:
    type: Literal["keypress"] = "keypress"
    keys: list["str"]

class Move:
    type: Literal["move"] = "move"
    x: int
    y: int
    keys: list[str] | None = None

class DoubleClick:
    type: Literal["double_click"] = "double_click"
    keys: list[str] | None
    x: int
    y: int

class Drag:
    type: Literal["drag"] = "drag"
    keys: list[str] | None

class Screenshot:
    type: Literal["screenshot"]

class Scroll:
    type: Literal["scroll"] = "scroll"
    scroll_x: int
    scroll_y: int
    x: int
    y: int
    keys: list[str] | None = None
    
class Wait:
    type: Literal["wait"] = "wait"

type OpenAIComputerAction = (
    Click
    | DoubleClick
    | Drag
    | Keypress
    | Move
    | Screenshot
    | Scroll
    | Type
    | Wait
)

class SafetyCheck:
    id: str
    code: str | None = None
    message: str | None = None

class Agent:
    agent_name: str

class OpenAIComputerUseToolCall(BaseModel):
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

class ComputerScreenshot:
    type: Literal["computer_screenshot"] = "computer_screenshot"
    file_id: str | None = None
    image_url: str | None = None

class OpenAIComputerUseToolResult:
    type: Literal["computer_call_output"] = "computer_call_output"
    call_id: str
    output: ComputerScreenshot
    acknowledged_safety_checks: list[SafetyCheck] | None



ant:
    AnthropicComputerUseTool:
        type: Literal["computer"]
        name: Literal["computer"]
        display_width_px: int
        display_height_px: int
        display_number: int
        enable_zoom: bool
    
    AnthropicComputerUseToolResult
        type: "screenshot" | "left_click" | "type"
'''