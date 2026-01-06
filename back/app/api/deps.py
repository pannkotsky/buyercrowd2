from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.apps.login.models import TokenPayload
from app.apps.login.utils import parse_token
from app.apps.users.crud import UserCrud
from app.apps.users.models import User
from app.core.config import settings
from app.core.db import engine

token_url = f"{settings.API_V1_STR}/login/access-token"
oauth2_optional = OAuth2PasswordBearer(tokenUrl=token_url, auto_error=False)
oauth2_required = OAuth2PasswordBearer(tokenUrl=token_url)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
OptionalTokenDep = Annotated[str | None, Depends(oauth2_optional)]
TokenDep = Annotated[str, Depends(oauth2_required)]


def parse_token_with_exception(token: str) -> TokenPayload:
    try:
        return parse_token(token)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


def get_optional_current_user(
    session: SessionDep, token: OptionalTokenDep
) -> User | None:
    if not token:
        return None
    token_data = parse_token_with_exception(token)
    if not token_data.sub:
        return None
    return UserCrud(session).read(id=token_data.sub)


OptionalCurrentUser = Annotated[User | None, Depends(get_optional_current_user)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    token_data = parse_token_with_exception(token)
    if not token_data.sub:
        raise HTTPException(status_code=404, detail="User not found")
    user = UserCrud(session).read(id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
