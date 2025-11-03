from dataclasses import dataclass


@dataclass(frozen=True)
class Site:
    id: int
    username: str
    password: str
    address: str
    max_connections_limit: int = 1
