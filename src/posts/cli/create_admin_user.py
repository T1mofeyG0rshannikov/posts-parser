import asyncio
from getpass import getpass

from dishka import make_async_container

from posts.ioc.db import DbProvider
from posts.ioc.ioc import UsecasesProvider
from posts.ioc.login import LoginProvider
from posts.ioc.web import WebProvider
from posts.usecases.create_user import CreateUser
from posts.user.validate_password import validate_password


async def create_admin_user(
    password: str,
    username: str,
    create_user: CreateUser,
) -> None:
    await create_user(
        password=password,
        username=username,
        is_superuser=True,
    )

    print(f"User '{username}' successfully created!")


def read_field(field_name: str, valid_func, read_func=input, mapped_func=str, mapped_func_args=[]) -> str:
    is_valid = False
    while not is_valid:
        try:
            field = mapped_func(read_func(f"Enter {field_name}: "), *mapped_func_args)
        except ValueError as e:
            print(e)
            continue

        is_valid = valid_func(field)
        if not is_valid:
            print(f"""Invalid {field_name} - "{field}". Try again""")

    return field


async def main():
    username = read_field(field_name="first name", valid_func=lambda un: len(un) > 0)
    password = read_field(field_name="password", valid_func=validate_password, read_func=getpass)

    container = make_async_container(UsecasesProvider(), DbProvider(), LoginProvider(), WebProvider())

    async with container() as request_container:
        create_user = await request_container.get(CreateUser)

        await create_admin_user(
            password=password,
            username=username,
            create_user=create_user,
        )


if __name__ == "__main__":
    asyncio.run(main())
