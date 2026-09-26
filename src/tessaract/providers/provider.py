from dataclasses import dataclass, field


@dataclass
class Provider:
    api_key: str | None = None
    base_url: str | None = None
    timeout: float | None = None
    max_retries: int | None = None
    default_headers: dict[str, str] | None = None
    default_query: dict[str, object] | None = None
    _client: object | None = None
    provider_args: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        raise NotImplementedError("not yet implemented")
    
    @property
    def client(self):
        raise NotImplementedError("not yet implemented")

    def _client_kwargs(self) -> dict:
        '''Keyword arguments for the SDK client: the typed fields that are set, overridden by provider_args.'''
        typed_args = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "default_headers": self.default_headers,
            "default_query": self.default_query,
        }

        return {
            **{key: value for key, value in typed_args.items() if value is not None},
            **self.provider_args,
        }
