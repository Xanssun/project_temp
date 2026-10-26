import uuid
from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.interfaces.hasher import AbstractHasher
from src.database.gateway import DBGateway
from src.database.models.types import RoleType
from src.database.repositories.types import CreateUserRoleType


class UpdateUserQuery(DTO):
    user_uuid: uuid.UUID
    login: str | None = None
    password: str | None = None
    active: bool | None = None
    subscription_auto_renewal: bool | None = None

    roles: set[RoleType] | None = None


class UpdateUserHandler(BaseHandler[UpdateUserQuery, dtos.PublicUser]):
    __slots__ = (
        "_db_gateway",
        "_hasher",
        "_role_repository",
        "_user_repository",
        "_user_role_repository",
    )

    def __init__(self, db_gateway: DBGateway, hasher: AbstractHasher) -> None:
        self._db_gateway = db_gateway
        self._hasher = hasher
        self._user_repository = db_gateway.user()
        self._role_repository = db_gateway.role()
        self._user_role_repository = db_gateway.user_role()

    async def handle(self, query: UpdateUserQuery, **kwargs: Any) -> dtos.PublicUser:
        data = query.model_dump(exclude_none=True, exclude={"user_uuid", "roles"})
        if password := data.get("password"):
            data["password"] = self._hasher.hash_password(password)

        async with self._db_gateway:
            roles = None
            if query.roles is not None:
                _, roles = await self._role_repository.select_many(
                    names=[role.value for role in query.roles],
                    limit=len(query.roles),
                )
                await self._user_role_repository.delete(
                    user_uuids=[query.user_uuid]
                )
                if roles:
                    await self._user_role_repository.create_many(
                        data=[
                            CreateUserRoleType(
                                user_uuid=query.user_uuid,
                                role_uuid=role.uuid,
                            )
                            for role in roles
                        ]
                    )

            user = await self._user_repository.update(query.user_uuid, **data)
            return dtos.PublicUser(
                uuid=user.uuid,
                login=user.login,
                active=user.active,
                subscription_auto_renewal=user.subscription_auto_renewal,
                roles=(
                    [dtos.Role(uuid=role.uuid, name=role.name) for role in roles]
                    if roles is not None
                    else None
                ),
            )
