'''
oai:
    OpenAIComputerUse:
        type: Literal["computer"] = "computer"

ComputerUseToolResult
    type
    call_id
    actions: list[Action]
    status

Action:
    Click(
        type: "click"
        button:
        x:
        y:
    )
    Type(
        type: "type"
        text: str
    )

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