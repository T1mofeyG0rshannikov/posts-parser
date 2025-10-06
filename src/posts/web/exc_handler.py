from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from posts.exceptions import (
    AccessDeniedError,
    RecordNotFoundError,
    UserWithUsernameAlreadyExistError,
)


async def access_denied_exc_handler(request: Request, exc: AccessDeniedError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": str(exc), "details": exc.message})


async def record_not_found_exc_handler(request: Request, exc: RecordNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": str(exc), "details": exc.message})


async def user_with_username_already_exist_exc_handler(
    request: Request, exc: UserWithUsernameAlreadyExistError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": str(exc), "details": exc.message})


def init_exc_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AccessDeniedError, access_denied_exc_handler)
    app.add_exception_handler(UserWithUsernameAlreadyExistError, user_with_username_already_exist_exc_handler)
    app.add_exception_handler(RecordNotFoundError, record_not_found_exc_handler)
