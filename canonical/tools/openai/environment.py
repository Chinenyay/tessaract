from typing import Literal

from pydantic import BaseModel


class NetworkPolicy(BaseModel):
    pass


class ContainerAuto:
    type: Literal["container_auto"] = "container_auto"

    network_policy: NetworkPolicy | None = None
    file_ids: list[str] | None = None
    memory_limit: Literal["1g", "4g", "16g", "64g"] | None = None
    # skills - TODO

class ContainerReference:
    type: Literal["container_reference"] = "container_reference"
    container_id: str

class NetworkAllowlist(NetworkPolicy):
    type: Literal["allowlist"] = "allowlist"

class NetworkDisabled(NetworkPolicy):
    type: Literal["disabled"] = "disabled"

class DomainSecret:
    domain: str
    name: str
    value: str

type Environment = ContainerReference | ContainerAuto