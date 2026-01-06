import uuid

from sqlmodel import Session, func, select

from app.apps.users.models import User, UserCreate, Users, UserUpdate, UserUpdateMe
from app.core.security import get_password_hash, verify_password


class UserCrud:
    def __init__(self, session: Session):
        self.session = session

    def list(self, skip: int = 0, limit: int = 100) -> Users:
        count_statement = select(func.count()).select_from(User)
        count = self.session.exec(count_statement).one()
        statement = select(User).offset(skip).limit(limit)
        users = self.session.exec(statement).all()
        return Users(data=users, count=count)

    def create(self, user_create: UserCreate) -> User:
        db_obj = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def update(self, db_user: User, user_in: UserUpdate) -> User:
        user_data = user_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        db_user.sqlmodel_update(user_data, update=extra_data)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def update_me(self, db_user: User, user_in: UserUpdateMe) -> User:
        user_data = user_in.model_dump(exclude_unset=True)
        db_user.sqlmodel_update(user_data)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def read(self, id: uuid.UUID | str) -> User | None:
        return self.session.get(User, id)

    def read_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        session_user = self.session.exec(statement).first()
        return session_user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()

    def update_password(self, user: User, new_password: str) -> None:
        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        self.session.add(user)
        self.session.commit()

    def authenticate(self, *, email: str, password: str) -> User | None:
        db_user = self.read_by_email(email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user
