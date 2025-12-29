from typing import TYPE_CHECKING

import strawberry
from graphql import GraphQLError
from sqlmodel import func, select
from strawberry.types import Info

from app.apps.users.models import User as UserModel

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

        session = info.context.db_session
        count_statement = select(func.count()).select_from(UserModel)

        count = session.exec(count_statement).one()

        statement = select(UserModel).offset(skip).limit(limit)
        users = session.exec(statement).all()

        return Users(
            data=[User.from_pydantic(user) for user in users],
            count=count,
        )
