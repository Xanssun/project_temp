from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.interfaces.hasher import AbstractHasher
from src.database.gateway import DBGateway
from src.database.repositories.types import CreateUserRoleType


class RegisterUserQuery(DTO):
    login: str
    password: str


class RegisterUserHandler(BaseHandler[RegisterUserQuery, dtos.Status]):
    def __init__(
        self,
        db_gateway: DBGateway,
        hasher: AbstractHasher,
    ) -> None:
        self._db_gateway = db_gateway
        self._hasher = hasher
        self._user_repository = db_gateway.user()
        self._role_repository = db_gateway.role()
        self._user_role_repository = db_gateway.user_role()

    async def handle(self, query: RegisterUserQuery, **kwargs: Any) -> dtos.Status:
        async with self._db_gateway:
            user = await self._user_repository.create(
                login=query.login,
                password=self._hasher.hash_password(query.password),
            )
            role = await self._role_repository.get(name="User")
            await self._user_role_repository.create(
                **CreateUserRoleType(user_uuid=user.uuid, role_uuid=role.uuid)
            )

        return dtos.Status(ok=True)
