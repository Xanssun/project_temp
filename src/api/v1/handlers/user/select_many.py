from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.database.gateway import DBGateway
from src.database.models.types import _UserLoadsType


class SelectUsersQuery(DTO):
    loads: tuple[_UserLoadsType, ...]
    login: str | None = None
    active: bool | None = None
    offset: int = 0
    limit: int = 10


class SelectManyUsershandler(BaseHandler[SelectUsersQuery, dtos.Users]):
    __slots__ = ("_db_gateway", "_user_repository")

    def __init__(self, db_gateway: DBGateway) -> None:
        self._db_gateway = db_gateway
        self._user_repository = db_gateway.user()

    async def handle(self, query: SelectUsersQuery, **kwargs: Any) -> dtos.Users:
        async with self._db_gateway:
            total, users = await self._user_repository.select_many(
                *query.loads,
                login=query.login,
                active=query.active,
                offset=query.offset,
                limit=query.limit,
            )
            return dtos.Users(
                data=[
                    dtos.PublicUser(
                        uuid=user.uuid,
                        login=user.login,
                        active=user.active,
                        subscription_auto_renewal=user.subscription_auto_renewal,
                        roles=(
                            [
                                dtos.Role(uuid=role.uuid, name=role.name)
                                for role in user.roles
                            ]
                            if "roles" in query.loads
                            else None
                        ),
                    )
                    for user in users
                ],
                total=total,
                offset=query.offset,
                limit=query.limit,
            )
