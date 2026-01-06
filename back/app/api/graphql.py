import uuid

import strawberry
from fastapi import Depends
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext, GraphQLRouter

from app.apps.items.graphql.query import Query as ItemsQuery
from app.apps.items.models import Item as ItemModel
from app.apps.users.graphql.loaders import load_items_by_owner_id, load_users
from app.apps.users.graphql.mutation import Mutation as UsersMutation
from app.apps.users.graphql.query import Query as UsersQuery
from app.apps.users.models import User as UserModel

from .deps import OptionalCurrentUser, SessionDep


class Context(BaseContext):
    """Global graphql context."""

    def __init__(
        self,
        db_session: SessionDep,
        current_user: OptionalCurrentUser,
    ) -> None:
        self.db_session = db_session
        self.current_user = current_user
        self.user_loader = DataLoader[uuid.UUID, UserModel | None](
            load_fn=lambda keys: load_users(keys, db_session),
        )
        self.items_by_owner_id_loader = DataLoader[uuid.UUID, list[ItemModel]](
            load_fn=lambda keys: load_items_by_owner_id(keys, db_session),
        )


def get_context(context: Context = Depends(Context)) -> Context:
    """
    Get custom context.

    :param context: graphql context.
    :return: context
    """
    return context


@strawberry.type
class Query(UsersQuery, ItemsQuery):
    """Main query."""


@strawberry.type
class Mutation(UsersMutation):
    """Main mutation."""


schema = strawberry.Schema(query=Query, mutation=Mutation)


gql_router = GraphQLRouter[Context, None](
    schema,
    graphiql=True,
    context_getter=get_context,
)
