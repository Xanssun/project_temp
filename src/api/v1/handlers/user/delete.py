import uuid
from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.database.gateway import DBGateway


class DeleteUserQuery(DTO):
    user_uuid: uuid.UUID | None = None
    login: str | None = None


class DeleteUserHandler(BaseHandler[DeleteUserQuery, dtos.PublicUser]):
    __slots__ = ("_db_gateway", "_user_repository")

    def __init__(self, db_gateway: DBGateway) -> None:
        self._db_gateway = db_gateway
        self._user_repository = db_gateway.user()

    async def handle(self, query: DeleteUserQuery, **kwargs: Any) -> dtos.PublicUser:
        async with self._db_gateway:
            user = await self._user_repository.delete(
                **query.model_dump(exclude_none=True), **kwargs
            )

            return dtos.PublicUser(
                uuid=user.uuid,
                login=user.login,
                active=user.active,
                subscription_auto_renewal=user.subscription_auto_renewal,
            )
