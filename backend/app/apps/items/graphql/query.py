from typing import TYPE_CHECKING

import strawberry
from graphql import GraphQLError
from sqlmodel import func, select
from strawberry.types import Info

from app.apps.items.models import Item as ItemModel

from .schema import Item, Items

if TYPE_CHECKING:
    from app.api.graphql import Context


@strawberry.type
class Query:
    @strawberry.field
    def items(self, info: Info["Context"], skip: int = 0, limit: int = 25) -> Items:
        user = info.context.current_user
        if not user or not user.is_superuser:
            raise GraphQLError("Forbidden")

        session = info.context.db_session
        count_statement = select(func.count()).select_from(ItemModel)

        count = session.exec(count_statement).one()

        statement = select(ItemModel).offset(skip).limit(limit)
        items = session.exec(statement).all()

        return Items(
            data=[Item.from_pydantic(item) for item in items],
            count=count,
        )
