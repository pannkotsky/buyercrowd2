import uuid

from sqlmodel import Session, func, select

from app.apps.items.models import Item, ItemCreate, Items, ItemUpdate


class ItemCrud:
    def __init__(self, session: Session):
        self.session = session

    def list(
        self,
        *,
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

        count = self.session.exec(count_statement).one()
        items = self.session.exec(statement).all()

        return Items(data=items, count=count)

    def read(self, id: uuid.UUID) -> Item | None:
        return self.session.get(Item, id)

    def create(self, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
        db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def update(self, item: Item, item_in: ItemUpdate) -> Item:
        update_dict = item_in.model_dump(exclude_unset=True)
        item.sqlmodel_update(update_dict)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete(self, item: Item) -> None:
        self.session.delete(item)
        self.session.commit()
