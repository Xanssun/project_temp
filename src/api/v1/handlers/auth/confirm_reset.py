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


class ConfirmResetRequestQuery(DTO):
    fingerprint: str
    password: str
    code: str


class ConfirmResetHandler(
    BaseHandler[ConfirmResetRequestQuery, dtos.TokensExpire]
):
    __slots__ = (
        "_cache",
        "_db_gateway",
        "_hasher",
        "_jwt",
        "_user_repository",
    )

    def __init__(
        self,
        db_gateway: DBGateway,
        hasher: AbstractHasher,
        redis: RedisCache,
        jwt: JWT,
    ) -> None:
        self._jwt = jwt
        self._db_gateway = db_gateway
        self._user_repository = db_gateway.user()
        self._hasher = hasher
        self._cache = redis

    async def handle(
        self, query: ConfirmResetRequestQuery, **kwargs: Any
    ) -> dtos.TokensExpire:
        user_data = await self._cache.get_single(query.code)
        if not user_data:
            raise BadRequestError("Invalid or expired code")
        await self._cache.delete(query.code)

        cached_user = dtos.ResetPassword.model_validate_json(user_data)

        async with self._db_gateway:
            user = await self._user_repository.get(login=cached_user.login)
            await self._user_repository.update(
                user.uuid,
                password=self._hasher.hash_password(query.password),
            )
            return await create_tokens(
                self._jwt,
                self._cache,
                user.uuid,
                query.fingerprint,
            )
