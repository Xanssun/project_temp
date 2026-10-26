import uuid
from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.database.gateway import DBGateway
from src.database.models.types import RoleType


class UpdateRoleQuery(DTO):
    role_uuid: uuid.UUID
    name: RoleType | None


class UpdateRoleHandler(BaseHandler[UpdateRoleQuery, dtos.Role]):
    __slots__ = ("_db_gateway", "_role_repository")

    def __init__(self, db_gateway: DBGateway) -> None:
        self._db_gateway = db_gateway
        self._role_repository = db_gateway.role()

    async def handle(self, query: UpdateRoleQuery, **kwargs: Any) -> dtos.Role:
        async with self._db_gateway:
            role = await self._role_repository.update(
                query.role_uuid,
                **query.model_dump(exclude_none=True, exclude={"role_uuid"}),
            )
            return dtos.Role(uuid=role.uuid, name=role.name)
