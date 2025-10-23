from dataclasses import dataclass
from typing import Any


@dataclass
class BaseOperationResult:
    success: bool


@dataclass
class OperationResult(BaseOperationResult):
    error_message: str | None = None
    data: Any | None = None
