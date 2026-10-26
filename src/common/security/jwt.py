import base64
from datetime import datetime, timedelta, timezone
from typing import (
    Any,
    Dict,
    Literal,
    Tuple,
)

import jwt

from src.common.dtos.token import Token
from src.common.exceptions import ConflictError, UnAuthorizedError
from src.core.settings import CipherSettings

TokenType = Literal["access", "refresh"]


class JWT:
    __slots__ = ("_settings",)

    def __init__(self, settings: CipherSettings) -> None:
        self._settings = settings

    def create(
        self,
        typ: TokenType,
        sub: str,
        expires_delta: timedelta | None = None,
        **kw: Any,
    ) -> Tuple[datetime, Token]:
        now = datetime.now(timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            match typ:
                case "access":
                    delta = timedelta(
                        seconds=self._settings.access_token_expire_seconds
                    )
                case "refresh":
                    delta = timedelta(
                        seconds=self._settings.refresh_token_expire_seconds
                    )
                case _:
                    raise UnAuthorizedError("Invalid token type")
            expire = now + delta

        if now >= expire:
            raise ConflictError("Invalid expiration delta was provided")

        to_encode = {
            "exp": expire,
            "sub": sub,
            "iat": now,
            "type": typ,
        }
        try:
            token = jwt.encode(
                to_encode | kw,
                base64.b64decode(self._settings.secret_key),
                self._settings.algorithm,
            )
        except jwt.PyJWTError as e:
            raise UnAuthorizedError("Token is expired") from e

        return expire, Token(token=token)

    def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            result = jwt.decode(
                token,
                base64.b64decode(self._settings.public_key),
                [self._settings.algorithm],
            )
        except jwt.PyJWTError as e:
            raise UnAuthorizedError("Token is invalid or expired") from e

        return result
