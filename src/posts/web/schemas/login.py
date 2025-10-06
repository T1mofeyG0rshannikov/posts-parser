from pydantic import BaseModel


class LoginResponse(BaseModel):
    ok: bool
    username_error_message: str | None = None
    password_error_message: str | None = None
