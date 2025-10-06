from pydantic import BaseModel


class ParseResponse(BaseModel):
    success: bool
    skipped: int
    inserted: int
