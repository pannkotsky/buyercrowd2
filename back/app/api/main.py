from fastapi import APIRouter

from app.apps.common.router import router as utils_router
from app.apps.items.router import router as items_router
from app.apps.login.router import router as login_router
from app.apps.users.private_router import router as private_users_router
from app.apps.users.router import router as users_router
from app.core.config import settings

from .graphql import gql_router

api_router = APIRouter()
api_router.include_router(login_router, tags=["login"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(utils_router, prefix="/utils", tags=["utils"])
api_router.include_router(items_router, prefix="/items", tags=["items"])

api_router.include_router(gql_router, prefix="/graphql", tags=["graphql"])

if settings.ENVIRONMENT == "local":
    private_router = APIRouter(prefix="/private", tags=["private"])
    private_router.include_router(private_users_router, prefix="/users")
    api_router.include_router(private_router)
