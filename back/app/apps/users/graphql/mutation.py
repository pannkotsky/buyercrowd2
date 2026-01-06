import uuid
from typing import TYPE_CHECKING

import strawberry
from graphql import GraphQLError
from strawberry.types import Info

from app.apps.users.crud import UserCrud
from app.apps.users.models import UpdatePassword, UserCreate, UserUpdate, UserUpdateMe
from app.core.security import verify_password
from app.graphql_utils import input_to_pydantic

from .schema import User

if TYPE_CHECKING:
    from app.api.graphql import Context


@strawberry.experimental.pydantic.input(model=UserCreate, all_fields=True)
class UserCreateInput:
    pass


@strawberry.experimental.pydantic.input(model=UpdatePassword, all_fields=True)
class UpdatePasswordInput:
    pass


@strawberry.input
class UpdateMeInput:
    full_name: strawberry.Maybe[str | None]
    email: strawberry.Maybe[str]


@strawberry.input
class UpdateUserInput:
    email: strawberry.Maybe[str]
    is_active: strawberry.Maybe[bool]
    is_superuser: strawberry.Maybe[bool]
    full_name: strawberry.Maybe[str | None]
    password: strawberry.Maybe[str]


@strawberry.type
class Mutation:
    @strawberry.field
    async def create_user(
        self,
        info: Info["Context"],
        input: UserCreateInput,
    ) -> User:
        current_user = info.context.current_user
        if not current_user or not current_user.is_superuser:
            raise GraphQLError("Forbidden")

        user = UserCrud(info.context.db_session).create(user_create=input.to_pydantic())
        return User.from_pydantic(user)

    @strawberry.field
    async def update_user(
        self,
        info: Info["Context"],
        user_id: uuid.UUID,
        input: UpdateUserInput,
    ) -> User:
        current_user = info.context.current_user
        if not current_user or not current_user.is_superuser:
            raise GraphQLError("Forbidden")

        user_crud = UserCrud(info.context.db_session)
        user = user_crud.read(id=user_id)
        if not user:
            raise GraphQLError("The user with this id does not exist in the system")

        user_in = input_to_pydantic(input, UserUpdate)
        if user_in.email:
            existing_user = user_crud.read_by_email(email=user_in.email)
            if existing_user and existing_user.id != user_id:
                raise GraphQLError("User with this email already exists")

        user = user_crud.update(db_user=user, user_in=user_in)
        return User.from_pydantic(user)

    @strawberry.field
    async def update_me(
        self,
        info: Info["Context"],
        input: UpdateMeInput,
    ) -> User:
        current_user = info.context.current_user
        if not current_user:
            raise GraphQLError("Unauthorized")

        user_in = input_to_pydantic(input, UserUpdateMe)
        current_user = UserCrud(info.context.db_session).update_me(
            db_user=current_user, user_in=user_in
        )
        return User.from_pydantic(current_user)

    @strawberry.field
    async def update_password_me(
        self,
        info: Info["Context"],
        input: UpdatePasswordInput,
    ) -> None:
        current_user = info.context.current_user
        if not current_user:
            raise GraphQLError("Unauthorized")

        passwords = input.to_pydantic()

        if not verify_password(
            passwords.current_password, current_user.hashed_password
        ):
            raise GraphQLError("Incorrect password")
        if passwords.current_password == passwords.new_password:
            raise GraphQLError("New password cannot be the same as the current one")

        UserCrud(info.context.db_session).update_password(
            user=current_user,
            new_password=passwords.new_password,
        )
