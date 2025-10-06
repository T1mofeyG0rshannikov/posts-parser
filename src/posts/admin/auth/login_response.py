from pydantic import BaseModel


class AdminLoginResponse(BaseModel):
    ok: bool
    username_error_message: str | None = None
    password_error_message: str | None = None
