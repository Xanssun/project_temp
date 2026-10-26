import uuid
from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.database.gateway import DBGateway
from src.database.models.types import PermissionType, _RoleLoadsType


class SelectRoleQuery(DTO):
    loads: tuple[_RoleLoadsType, ...]
    role_uuid: uuid.UUID | None = None
    name: PermissionType | None = None


class SelectRoleHandler(BaseHandler[SelectRoleQuery, dtos.Role]):
    __slots__ = ("_db_gateway", "_role_repository")

    def __init__(self, db_gateway: DBGateway) -> None:
        self._db_gateway = db_gateway
        self._role_repository = db_gateway.role()

    async def handle(self, query: SelectRoleQuery, **kwargs: Any) -> dtos.Role:
        async with self._db_gateway:
            role = await self._role_repository.get(
                *query.loads, role_uuid=query.role_uuid, name=query.name
            )
            return dtos.Role(
                uuid=role.uuid,
                name=role.name,
                users=(
                    [
                        dtos.PublicUser(
                            uuid=user.uuid,
                            login=user.login,
                            active=user.active,
                            subscription_auto_renewal=user.subscription_auto_renewal,
                        )
                        for user in role.users
                    ]
                    if "users" in query.loads
                    else None
                ),
            )
