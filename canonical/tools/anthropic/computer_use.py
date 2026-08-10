from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from ..computer_use import ComputerUseTool


class AnthropicComputerUseToolType(StrEnum):
    type_v1 = "computer_20250124"
    type_v2 = "computer_20251124"

class AnthropicComputerUseToolParams(BaseModel):
    type: AnthropicComputerUseToolType
    name: Literal["computer"] = "computer"

    display_width_px: int
    display_height_px: int

    display_number: int | None = None
    enable_zoom: bool = False

class AnthropicCursorPosition:
    action: Literal['cursor_position'] = 'cursor_position'


class AnthropicScreenshot:
    action: Literal['screenshot'] = 'screenshot'

class AnthropicLeftClick:
    action: Literal['left_click'] = 'left_click'
    coordinate: tuple[int, int]
    key: str | None = None

class AnthropicType:
    action: Literal['type'] = 'type'
    text: str

AnthropicScrollDirection = Literal[
    'up',
    'down',
    'left',
    'right'
]

class AnthropicScroll:
    action: Literal['scroll'] = 'scroll'
    coordinate: tuple[int, int] | None = None
    scroll_direction: AnthropicScrollDirection
    scroll_amount: int
    text: str | None = None

class AnthropicZoom(BaseModel):
    action: Literal['zoom'] = 'zoom'
    region: tuple[int, int, int, int] = Field(gt=0)

class AnthropicHoldKey(BaseModel):
    action: Literal['hold_key'] = 'hold_key'
    duration: int | float = Field(ge=0)
    text: str

class AnthropicWait:
    action: Literal['wait'] = 'wait'
    duration: int | float = Field(ge=0)

class AnthropicRightClick:
    action: Literal['right_click'] = 'right_click'
    coordinate: tuple[int, int]
    key: str | None = None

class AnthropicDoubleClick:
    action: Literal['left_click'] = 'left_click'
    coordinate: tuple[int, int]
    key: str | None = None

class AnthropicTripleClick:
    action: Literal['triple_click'] = 'triple_click'
    coordinate: tuple[int, int]
    key: str | None = None

class AnthropicMiddleClick:
    action: Literal['middle_click'] = 'middle_click'
    coordinate: tuple[int, int]
    key: str | None = None

class AnthropicLeftClickDrag:
    action: Literal['left_click_drag'] = 'left_click_drag'
    coordinate: tuple[int, int]
    start_coordinate: tuple[int, int]

class AnthropicMouseMove:
    action: Literal['mouse_move'] = 'mouse_move'
    coordinate: tuple[int, int]

class AnthropicKey:
    action: Literal['key'] = 'key'
    text: str

class AnthropicLeftMouseDown:
    action: Literal['left_mouse_down'] = 'left_mouse_down'

class AnthropicLeftMouseUp:
    action: Literal['left_mouse_up'] = 'left_mouse_up'


AnthropicComputerAction = (
        AnthropicScreenshot
        | AnthropicLeftClick
        | AnthropicType
        | AnthropicKey
        | AnthropicMouseMove
        | AnthropicScroll
        | AnthropicLeftClickDrag
        | AnthropicWait
        | AnthropicLeftMouseDown
        | AnthropicLeftMouseUp
        | AnthropicHoldKey
        | AnthropicZoom
        | AnthropicMiddleClick
        | AnthropicRightClick
        | AnthropicDoubleClick
        | AnthropicTripleClick
        | AnthropicCursorPosition
    )

class AnthropicComputerUseTool(ComputerUseTool):
    type: Literal['tool_use']
    id: str
    name: Literal['computer']
    input: AnthropicComputerAction


