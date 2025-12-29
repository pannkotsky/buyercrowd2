import uuid
from collections import defaultdict
from typing import TYPE_CHECKING

from sqlmodel import select

from app.apps.items.models import Item as ItemModel
from app.apps.users.models import User as UserModel

if TYPE_CHECKING:
    from sqlmodel import Session


async def load_users(
    keys: list[uuid.UUID], db_session: "Session"
) -> list[UserModel | None]:
    """Batch load multiple users by IDs."""
    statement = select(UserModel).where(
        UserModel.id.in_(keys)  # type: ignore[attr-defined]
    )
    users = db_session.exec(statement).all()

    # Create a mapping of ID to user
    user_map = {user.id: user for user in users}

    # Return users in the same order as keys, with None for missing ones
    return [user_map.get(key) for key in keys]


async def load_items_by_owner_id(
    keys: list[uuid.UUID], db_session: "Session"
) -> list[list[ItemModel]]:
    """Batch load multiple items by owner IDs."""
    statement = select(ItemModel).where(
        ItemModel.owner_id.in_(keys)  # type: ignore[attr-defined]
    )
    items = db_session.exec(statement).all()
    item_map = defaultdict(list)
    for item in items:
        item_map[item.owner_id].append(item)
    return [item_map[key] for key in keys]
