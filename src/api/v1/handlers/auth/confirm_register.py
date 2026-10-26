from typing import Any

from src.api.common.cache.redis import RedisCache
from src.api.v1.handlers.auth.tools import create_tokens
from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import BadRequestError
from src.common.interfaces.hasher import AbstractHasher
from src.common.security.jwt import JWT
from src.database.gateway import DBGateway
from src.database.repositories.types import CreateUserRoleType


class ConfirmRequestQuery(DTO):
    code: str
    fingerprint: str


class ConfirmRegistrationHandler(BaseHandler[ConfirmRequestQuery, dtos.TokensExpire]):
    __slots__ = (
        "_cache",
        "_db_gateway",
        "_hasher",
        "_jwt",
        "_role_repository",
        "_user_repository",
        "_user_role_repository",
    )

    def __init__(
        self,
        db_gateway: DBGateway,
        hasher: AbstractHasher,
        redis: RedisCache,
        jwt: JWT,
    ) -> None:
        self._db_gateway = db_gateway
        self._user_repository = db_gateway.user()
        self._role_repository = db_gateway.role()
        self._user_role_repository = db_gateway.user_role()
        self._hasher = hasher
        self._cache = redis
        self._jwt = jwt

    async def handle(
        self, query: ConfirmRequestQuery, **kwargs: Any
    ) -> dtos.TokensExpire:
        user_data = await self._cache.get_single(query.code)

        if not user_data:
            raise BadRequestError("Invalid or expired code")

        await self._cache.delete(query.code)

        cached_user = dtos.RegisterUser.model_validate_json(user_data)

        async with self._db_gateway:
            role = await self._role_repository.get(name="User")
            user = await self._user_repository.create(
                login=cached_user.login,
                password=self._hasher.hash_password(cached_user.password),
            )

            await self._user_role_repository.create(
                **CreateUserRoleType(
                    user_uuid=user.uuid,
                    role_uuid=role.uuid,
                )
            )

            return await create_tokens(
                self._jwt,
                self._cache,
                user.uuid,
                query.fingerprint,
            )
