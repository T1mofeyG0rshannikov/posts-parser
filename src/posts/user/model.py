from dataclasses import dataclass


@dataclass
class User:
    username: str
    hash_password: str
    is_superuser: bool
    id: int | None = None
