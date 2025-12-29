from typing import TYPE_CHECKING, Annotated

import strawberry
from strawberry.types import Info

from app.apps.items.models import Item as ItemModel

if TYPE_CHECKING:
    from app.api.graphql import Context
    from app.apps.users.graphql.schema import User


@strawberry.experimental.pydantic.type(
    model=ItemModel, fields=["id", "title", "description", "owner_id"]
)
class Item:
    @strawberry.field
    async def owner(
        self, info: Info["Context"]
    ) -> Annotated["User", strawberry.lazy("app.apps.users.graphql.schema")]:
        from app.apps.users.graphql.schema import User

        user_loader = info.context.user_loader
        owner_instance = await user_loader.load(
            self.owner_id  # type: ignore[attr-defined]
        )

        if owner_instance is None:
            raise ValueError("Item owner not found")

        return User.from_pydantic(owner_instance)


@strawberry.type
class Items:
    data: list[Item]
    count: int
