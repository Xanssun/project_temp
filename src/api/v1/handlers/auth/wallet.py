from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import ServiceNotImplementedError


class LoginViaWalletQuery(DTO):
    message: str
    signature: str
    address: str
    fingerprint: str


class LoginViaWalletHandler(
    BaseHandler[LoginViaWalletQuery, dtos.TokensExpire]
):
    async def handle(
        self, query: LoginViaWalletQuery, **kwargs: Any
    ) -> dtos.TokensExpire:
        raise ServiceNotImplementedError(
            "Wallet authentication requires a wallet storage model"
        )
