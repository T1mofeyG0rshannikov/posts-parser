from dataclasses import dataclass


@dataclass
class Site:
    username: str
    password: str
    address: str
