class AccessDeniedError(Exception):
    pass


class RecordNotFoundError(Exception):
    pass


class UserNotFoundError(RecordNotFoundError):
    pass


class InvalidPasswordError(AccessDeniedError):
    pass


class UserWithUsernameAlreadyExistError(Exception):
    pass


class NotPermittedError(Exception):
    pass


class PostNotFoundError(RecordNotFoundError):
    pass


class TagNotFoundError(RecordNotFoundError):
    pass


class PostAlreadyHasTagError(Exception):
    pass
