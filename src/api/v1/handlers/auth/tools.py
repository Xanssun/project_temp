from datetime import UTC, datetime
from uuid import UUID

from src.api.common.cache.redis import RedisCache
from src.common import dtos
from src.common.exceptions import UnAuthorizedError
from src.common.security.jwt import JWT, TokenType


def refresh_token_key(token: str) -> str:
    return f"auth:refresh:{token}"


async def create_tokens(
    jwt: JWT,
    cache: RedisCache,
    user_uuid: UUID,
    fingerprint: str,
) -> dtos.TokensExpire:
    _, access = jwt.create("access", str(user_uuid), fingerprint=fingerprint)
    refresh_expire, refresh = jwt.create(
        "refresh", str(user_uuid), fingerprint=fingerprint
    )
    expires_in = int((refresh_expire - datetime.now(UTC)).total_seconds())
    await cache.set_single(
        refresh_token_key(refresh.token),
        str(user_uuid),
        expire_seconds=expires_in,
    )
    return dtos.TokensExpire(
        refresh_expire=refresh_expire,
        tokens=dtos.Tokens(access=access.token, refresh=refresh.token),
    )


async def verify_token(
    jwt: JWT,
    cache: RedisCache,
    token: str,
    token_type: TokenType,
) -> UUID:
    payload = jwt.verify_token(token)
    if payload.get("type") != token_type:
        raise UnAuthorizedError("Invalid token type")
    if token_type == "refresh" and not await cache.get_single(
        refresh_token_key(token)
    ):
        raise UnAuthorizedError("Refresh token is invalidated")
    return UUID(payload["sub"])
