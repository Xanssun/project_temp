from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import NotFoundError
from src.common.interfaces.hasher import AbstractHasher
from src.database.gateway import DBGateway
from src.database.models.types import RoleType
from src.database.repositories.types import CreateUserRoleType


class CreateUserQuery(DTO):
    login: str
    password: str
    roles: set[RoleType]


class CreateUserHandler(BaseHandler[CreateUserQuery, dtos.PublicUser]):
    __slots__ = (
        "_db_gateway",
        "_hasher",
        "_role_repository",
        "_user_repository",
        "_user_role_repository",
    )

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

    async def handle(self, query: CreateUserQuery, **kwargs: Any) -> dtos.PublicUser:
        password_hash = self._hasher.hash_password(query.password)

        async with self._db_gateway:
            _, roles = await self._role_repository.select_many(
                names=[role.value for role in query.roles],
                limit=len(query.roles),
            )

            found_roles = {role.name for role in roles}
            missing_roles = query.roles - found_roles
            if missing_roles:
                names = ", ".join(sorted(role.value for role in missing_roles))
                raise NotFoundError(f"Roles not found: {names}")

            user = await self._user_repository.create(
                login=query.login,
                password=password_hash,
                **kwargs,
            )

            if roles:
                await self._user_role_repository.create_many(
                    data=[
                        CreateUserRoleType(
                            user_uuid=user.uuid,
                            role_uuid=role.uuid,
                        )
                        for role in roles
                    ]
                )

            return dtos.PublicUser(
                uuid=user.uuid,
                login=user.login,
                active=user.active,
                subscription_auto_renewal=user.subscription_auto_renewal,
                roles=[
                    dtos.Role(uuid=role.uuid, name=role.name)
                    for role in roles
                ],
            )
