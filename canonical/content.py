
from dataclasses import dataclass


@dataclass(frozen=True)
class ContentPart:
    pass

class TextPart(ContentPart):
    text: str

@dataclass(frozen=True)
class URLSource:
    url: str
    media_type: str | None = None

@dataclass(frozen=True)
class ByteSource:
    bytes: str
    media_type: str | None = None

@dataclass(frozen=True)
class ProviderFileSource:
    provider: str
    file_id: str
    media_type: str | None = None

MediaSource = URLSource | ByteSource | ProviderFileSource


class ImagePart(ContentPart):
    source: MediaSource

class FilePart(ContentPart):
    source: MediaSource

class AudioPart(ContentPart):
    source: MediaSource

'''
Desired shape
    TextPart("hello")
    ImagePart("url=xyz...")
'''

