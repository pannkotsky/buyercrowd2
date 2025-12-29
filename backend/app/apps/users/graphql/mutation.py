from typing import TYPE_CHECKING

import strawberry
from graphql import GraphQLError
from pydantic import ValidationError
from strawberry.types import Info

from app.apps.users.models import UserUpdateMe

from .schema import User

if TYPE_CHECKING:
    from app.api.graphql import Context


@strawberry.input
class UserUpdateMeInput:
    full_name: str | None = strawberry.UNSET
    email: str | None = strawberry.UNSET


@strawberry.type
class Mutation:
    @strawberry.field
    async def update_me(
        self, info: Info["Context"], user_in: UserUpdateMeInput
    ) -> User:
        current_user = info.context.current_user
        if not current_user:
            raise GraphQLError("Unauthorized")

        session = info.context.db_session

        # Build dict with only fields that were explicitly provided (not UNSET)
        input_data = {}
        if user_in.full_name is not strawberry.UNSET:
            input_data["full_name"] = user_in.full_name
        if user_in.email is not strawberry.UNSET:
            input_data["email"] = user_in.email

        # Validate using Pydantic model (handles email format and max_length)
        try:
            validated = UserUpdateMe.model_validate(input_data)
            user_data = validated.model_dump(exclude_unset=True)
        except ValidationError as e:
            # Convert Pydantic validation errors to GraphQL errors
            errors = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                msg = error["msg"]
                errors.append(f"{field}: {msg}")
            raise GraphQLError(f"Validation error: {', '.join(errors)}") from e

        current_user.sqlmodel_update(user_data)
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        return User.from_pydantic(current_user)
