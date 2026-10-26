from fastapi import APIRouter

from .role import role_router
from .user import user_router

admin_router = APIRouter(prefix="/admin")
admin_router.include_router(role_router)
admin_router.include_router(user_router)
