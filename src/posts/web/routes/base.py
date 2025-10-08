from collections.abc import Callable
from functools import wraps
from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from starlette.requests import Request

from posts.exceptions import NotPermittedError
from posts.persistence.data_mappers.user_data_mapper import UserDataMapper
from posts.persistence.models import UserOrm
from posts.user.auth.jwt_processor import JwtProcessor
from posts.user.model import User


def admin_required(func: Callable) -> Callable:
    def wrapper(func: Callable):
        @wraps(func)
        async def wrapped_func(*args, user: User, **kwargs):
            if user and not user.is_superuser or not user:
                raise NotPermittedError("у вас нет прав для выполнения запроса")
            return await func(*args, user=user, **kwargs)

        return wrapped_func

    return wrapper(func)


@inject
async def get_user(
    request: Request,
    jwt_processor: FromDishka[JwtProcessor],
    user_data_mapper: FromDishka[UserDataMapper],
) -> UserOrm:
    token = request.session.get("token")
    if token:
        payload = jwt_processor.validate_token(token)
        if payload:
            return await user_data_mapper.get(payload["id"])

    return None


UserAnnotation = Annotated[User, Depends(get_user)]
