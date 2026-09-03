from typing_extensions import Protocol

from dataclasses import dataclass, field


@dataclass
class Provider:
    api_key: str | None = None
    base_url: str | None = None
    timeout: int | None = None
    max_retries: int | None = None
    default_headers: str | None = None
    default_query: int | None = None
    _client: object | None = None
    provider_args: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        raise NotImplementedError("not yet implemented")
    
    @property
    def client(self):
        raise NotImplementedError("not yet implemented")

    def map_input_message(self):