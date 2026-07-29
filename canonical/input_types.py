from abc import ABC
from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class Message(ABC):
    pass
    

@dataclass(frozen=True)
class Input(Message):
    @property
    def type(self):
        pass


@dataclass(frozen=True)
class TextInput(Input):
    content: str

    @property
    def type(self):
        return "input_text"

@dataclass(frozen=True)
class ImageInput(Input):
    path: str

    @property
    def type(self):
        return "image"


@dataclass(frozen=True)
class ToolObject:
    pass

@dataclass(frozen=True)
class ToolInput(Input):
    # tool attributes: name, description, type, parameters: type, description
    pass

    @property
    def type(self):
        pass


@dataclass(frozen=True)
class ToolCallResult(ToolInput):
    @property
    def type(self):
        return "tool_call_result"

@dataclass(frozen=True)
class ToolResultInput(ToolInput):

    @property
    def type(self):
        return "tool_result_input"

@dataclass
class FileInput:
    path: str

    @property
    def type(self):
        '''The canonical file type. All FileInput objects are input_file types by default.'''
        return "input_file"
    

    # @property
    # def filetype(self):
    #     '''Returns the file extension to identify the real file type'''
    #     ext = utils.get_file_extension(self.path)
    #     return f"{ext}_input"

class Roles(Enum):
    user = "user"
    assistant = "assistant"
    system = "system"
    developer = "developer"
