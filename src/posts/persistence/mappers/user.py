from posts.persistence.models import UserOrm
from posts.user.model import User


def from_orm_to_user(user: UserOrm) -> User:
    return User(id=user.id, username=user.username, hash_password=user.hash_password, is_superuser=user.is_superuser)
