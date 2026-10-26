import uuid
from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.database.gateway import DBGateway
from src.database.models.types import _UserLoadsType


class SelectUserQuery(DTO):
    loads: tuple[_UserLoadsType, ...]
    user_uuid: uuid.UUID | None = None
    login: str | None = None


class SelectUserHandler(BaseHandler[SelectUserQuery, dtos.PublicUser]):
    __slots__ = ("_db_gateway", "_user_repository")

    def __init__(self, db_gateway: DBGateway) -> None:
        self._db_gateway = db_gateway
        self._user_repository = db_gateway.user()

    async def handle(self, query: SelectUserQuery, **kwargs: Any) -> dtos.PublicUser:
        async with self._db_gateway:
            user = await self._user_repository.get(
                *query.loads, user_uuid=query.user_uuid, login=query.login
            )
            return dtos.PublicUser(
                uuid=user.uuid,
                login=user.login,
                active=user.active,
                subscription_auto_renewal=user.subscription_auto_renewal,
                roles=(
                    [dtos.Role(uuid=role.uuid, name=role.name) for role in user.roles]
                    if "roles" in query.loads
                    else None
                ),
            )
