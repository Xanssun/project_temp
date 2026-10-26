from typing import Any

from src.api.common.cache.redis import RedisCache
from src.api.v1.handlers.auth.tools import create_tokens
from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import ForbiddenError, UnAuthorizedError
from src.common.interfaces.hasher import AbstractHasher
from src.common.security.jwt import JWT
from src.database.gateway import DBGateway


class LoginQuery(DTO):
    login: str
    password: str
    fingerprint: str


class LoginHandler(BaseHandler[LoginQuery, dtos.TokensExpire]):
    def __init__(
        self,
        db_gateway: DBGateway,
        hasher: AbstractHasher,
        jwt: JWT,
        redis: RedisCache,
    ) -> None:
        self._jwt = jwt
        self._cache = redis
        self._hasher = hasher
        self._db_gateway = db_gateway
        self._user_repository = db_gateway.user()

    async def handle(self, query: LoginQuery, **kwargs: Any) -> dtos.TokensExpire:
        async with self._db_gateway:
            user = await self._user_repository.get(login=query.login)

            if not user.active:
                raise ForbiddenError("You have been blocked")
            if not self._hasher.verify_password(user.password, query.password):
                raise UnAuthorizedError("Incorrect password")

            return await create_tokens(
                self._jwt,
                self._cache,
                user.uuid,
                query.fingerprint,
            )
