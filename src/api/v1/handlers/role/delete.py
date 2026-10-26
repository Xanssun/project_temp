import uuid
from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.database.gateway import DBGateway


class DeleteRoleQuery(DTO):
    role_uuid: uuid.UUID | None = None


class DeleteRoleHandler(BaseHandler[DeleteRoleQuery, dtos.Role]):
    __slots__ = ("_db_gateway", "_role_repository")

    def __init__(self, db_gateway: DBGateway) -> None:
        self._db_gateway = db_gateway
        self._role_repository = db_gateway.role()

    async def handle(self, query: DeleteRoleQuery, **kwargs: Any) -> dtos.Role:
        async with self._db_gateway:
            role = await self._role_repository.delete(**query.model_dump())
            return dtos.Role(uuid=role.uuid, name=role.name)
