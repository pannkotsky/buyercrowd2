import uuid
from typing import TYPE_CHECKING

import strawberry
from graphql import GraphQLError
from strawberry.types import Info

from app.apps.users import crud

from .schema import User, Users

if TYPE_CHECKING:
    from app.api.graphql import Context


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: Info["Context"]) -> User | None:
        user = info.context.current_user
        return user and User.from_pydantic(user)

    @strawberry.field
    async def users(
        self, info: Info["Context"], skip: int = 0, limit: int = 25
    ) -> Users:
        user = info.context.current_user
        if not user or not user.is_superuser:
            raise GraphQLError("Forbidden")

        users = crud.get_users(session=info.context.db_session, skip=skip, limit=limit)

        return Users(
            data=[User.from_pydantic(user) for user in users.data],
            count=users.count,
        )

    @strawberry.field
    async def user(self, info: Info["Context"], user_id: uuid.UUID) -> User | None:
        current_user = info.context.current_user
        if not current_user or (
            user_id != current_user.id and not current_user.is_superuser
        ):
            raise GraphQLError("Forbidden")

        user = crud.get_user_by_id(session=info.context.db_session, id=user_id)
        return user and User.from_pydantic(user)
