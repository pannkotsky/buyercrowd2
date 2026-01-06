from sqlmodel import Session

from app.apps.items.crud import ItemCrud
from app.apps.items.models import Item, ItemCreate
from app.apps.users.tests.utils import create_random_user
from app.test_utils import random_lower_string


def create_random_item(session: Session) -> Item:
    user = create_random_user(session)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    return ItemCrud(session).create(item_in=item_in, owner_id=owner_id)
