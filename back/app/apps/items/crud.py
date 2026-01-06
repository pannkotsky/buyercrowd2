import uuid

from sqlmodel import Session, func, select

from app.apps.items.models import Item, ItemCreate, Items, ItemUpdate


def get_items(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: uuid.UUID | None = None,
) -> Items:
    if user_id:
        count_statement = (
            select(func.count()).select_from(Item).where(Item.owner_id == user_id)
        )
        statement = (
            select(Item).where(Item.owner_id == user_id).offset(skip).limit(limit)
        )
    else:
        count_statement = select(func.count()).select_from(Item)
        statement = select(Item).offset(skip).limit(limit)

    count = session.exec(count_statement).one()
    items = session.exec(statement).all()

    return Items(data=items, count=count)


def get_item_by_id(*, session: Session, id: uuid.UUID) -> Item | None:
    return session.get(Item, id)


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def update_item(*, session: Session, item: Item, item_in: ItemUpdate) -> Item:
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_item(*, session: Session, item: Item) -> None:
    session.delete(item)
    session.commit()
