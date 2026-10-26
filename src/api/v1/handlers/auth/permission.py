from typing import Any

from src.api.common.cache.redis import RedisCache
from src.api.v1.handlers.auth.tools import verify_token
from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import (
    ForbiddenError,
    ServiceNotImplementedError,
    UnAuthorizedError,
)
from src.common.security.jwt import JWT
from src.database.gateway import DBGateway
from src.database.models.types import PermissionType


class PermissionQuery(DTO):
    permissions: tuple[PermissionType | None, ...]
    excluede_permissions: tuple[PermissionType | None, ...] = ()
    access_token: str | None
    refresh_token: str


class PermissionHandler(BaseHandler[PermissionQuery, dtos.PrivateUser]):
    def __init__(
        self,
        db_gateway: DBGateway,
        jwt: JWT,
        redis: RedisCache,
    ) -> None:
        self._db_gateway = db_gateway
        self._user_repository = db_gateway.user()
        self._jwt = jwt
        self._cache = redis

    async def handle(self, query: PermissionQuery, **kwargs: Any) -> dtos.PrivateUser:
        if query.access_token:
            user_uuid = await verify_token(
                self._jwt, self._cache, query.access_token, "access"
            )
        else:
            user_uuid = await verify_token(
                self._jwt, self._cache, query.refresh_token, "refresh"
            )

        async with self._db_gateway:
            user = await self._user_repository.get(
                "roles", user_uuid=user_uuid, **kwargs
            )

        if not user.active:
            raise ForbiddenError("You have been blocked")
        if not user.roles:
            raise ServiceNotImplementedError("Roles not found")

        excluded_permission_set = set(query.excluede_permissions)
        allowed_permissions_set = set(query.permissions)

        for role in user.roles:
            if role.name in excluded_permission_set:
                raise UnAuthorizedError("Not Allowed")

        if not allowed_permissions_set:
            authorized = True
        else:
            authorized = any(
                role.name in allowed_permissions_set for role in user.roles
            )

        if not authorized:
            raise UnAuthorizedError("Not Allowed")

        return dtos.PrivateUser(
            uuid=user.uuid,
            login=user.login,
            password=user.password,
            active=user.active,
            subscription_auto_renewal=user.subscription_auto_renewal,
            roles=[
                dtos.Role(uuid=role.uuid, name=role.name)
                for role in user.roles
            ],
            access_token=query.access_token,
            refresh_token=query.refresh_token,
        )
