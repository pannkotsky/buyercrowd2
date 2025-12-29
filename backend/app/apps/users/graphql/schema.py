from typing import TYPE_CHECKING, Annotated

import strawberry
from strawberry.types import Info

from app.apps.users.models import User as UserModel

if TYPE_CHECKING:
    from app.api.graphql import Context
    from app.apps.items.graphql.schema import Item


@strawberry.experimental.pydantic.type(
    model=UserModel,
    fields=[
        "id",
        "email",
        "is_active",
        "is_superuser",
        "full_name",
    ],
)
class User:
    @strawberry.field
    async def items(
        self, info: Info["Context"]
    ) -> list[Annotated["Item", strawberry.lazy("app.apps.items.graphql.schema")]]:
        from app.apps.items.graphql.schema import Item

        items_loader = info.context.items_by_owner_id_loader
        items = await items_loader.load(self.id)  # type: ignore[attr-defined]
        return [Item.from_pydantic(item) for item in items]


@strawberry.type
class Users:
    data: list[User]
    count: int
