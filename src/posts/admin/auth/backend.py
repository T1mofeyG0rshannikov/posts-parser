from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from posts.admin.auth.login_factory.dishka_login_factory import LoginFactory
from posts.admin.auth.login_response import AdminLoginResponse
from posts.admin.config import AdminConfig
from posts.exceptions import AccessDeniedError, InvalidPasswordError, UserNotFoundError
from posts.user.auth.jwt_processor import JwtProcessor
from posts.user.password_hasher import PasswordHasher


class AdminAuth(AuthenticationBackend):
    def __init__(
        self,
        password_hasher: PasswordHasher,
        config: AdminConfig,
        jwt_processor: JwtProcessor,
        login_factory: LoginFactory,
    ) -> None:
        super().__init__(config.secret_key)
        self.password_hasher = password_hasher
        self.jwt_processor = jwt_processor
        self.config = config
        self.login_factory = login_factory

    async def login(self, request: Request) -> AdminLoginResponse:
        login = await self.login_factory()

        form = await request.form()
        username, password = form["username"], form["password"]

        try:
            access_token = await login(username, password)
            request.session.update({"token": access_token})
            return AdminLoginResponse(ok=True)
        except (UserNotFoundError, InvalidPasswordError) as e:
            return AdminLoginResponse(ok=False, username_error_message=str(e))
        except AccessDeniedError:
            return AdminLoginResponse(
                ok=False, username_error_message="Недостаточно прав для входа в панель администратора"
            )

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if token and self.jwt_processor.validate_token(token):
            return True

        return False
