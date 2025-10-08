from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from posts.exceptions import (
    AccessDeniedError,
    PostAlreadyHasTagError,
    RecordNotFoundError,
    UserWithUsernameAlreadyExistError,
)


async def access_denied_exc_handler(request: Request, exc: AccessDeniedError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"error": str(exc)})


async def record_not_found_exc_handler(request: Request, exc: RecordNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": str(exc)})


async def user_with_username_already_exist_exc_handler(
    request: Request, exc: UserWithUsernameAlreadyExistError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": str(exc)})


async def post_already_has_tag_exc_handler(request: Request, exc: PostAlreadyHasTagError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": str(exc)})


def init_exc_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AccessDeniedError, access_denied_exc_handler)
    app.add_exception_handler(UserWithUsernameAlreadyExistError, user_with_username_already_exist_exc_handler)
    app.add_exception_handler(RecordNotFoundError, record_not_found_exc_handler)
    app.add_exception_handler(PostAlreadyHasTagError, post_already_has_tag_exc_handler)
