from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.database.gateway import DBGateway
from src.database.models.types import RoleType


class CreateRoleQuery(DTO):
    name: RoleType


class CreateRoleHandler(BaseHandler[CreateRoleQuery, dtos.Role]):
    __slots__ = ("_db_gateway", "_role_repository")

    def __init__(self, db_gateway: DBGateway) -> None:
        self._db_gateway = db_gateway
        self._role_repository = db_gateway.role()

    async def handle(self, query: CreateRoleQuery, **kwargs: Any) -> dtos.Role:
        async with self._db_gateway:
            role = await self._role_repository.create(name=query.name)
            return dtos.Role(uuid=role.uuid, name=role.name)
