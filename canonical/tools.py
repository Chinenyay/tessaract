from dataclasses import dataclass
from typing import Any, TypeAlias, Mapping
from .content import ContentPart

@dataclass(frozen=True)
class ToolCallPart(ContentPart):
    pass

JSONSchema: TypeAlias = Mapping[str, Any]

class FunctionTool(ContentPart):
    name: str
    description: str
    input_schema: JSONSchema

class ToolResult(ContentPart):
    pass

'''
# OPENAI TOOL SHAPE
tools = [
    {
        "type": "function",
        "name": "get_horoscope",
        "description": "Get today's horoscope for an astrological sign.",
        "parameters": {
            "type": "object",
            "properties": {
                "sign": {
                    "type": "string",
                    "description": "An astrological sign like Taurus or Aquarius",
                },
            },
            "required": ["sign"],
        },
    },
]

tools = [
    {
        "name": "get_stock_price",
        "description": "Retrieves the current stock price for a given ticker symbol. The ticker symbol must be a valid symbol for a publicly traded company on a major US stock exchange like NYSE or NASDAQ. The tool will return the latest trade price in USD. It should be used when the user asks about the current or most recent price of a specific stock. It will not provide any other information about the stock or company.",
        "input_schema": {
            "type": "object",
            "properties": {
            "ticker": {
                "type": "string",
                "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
            }
            },
            "required": ["ticker"]
        }
    }
]

'''