from typing import Any

from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import ServiceNotImplementedError


class ConfirmTwoFaCodeQuery(DTO):
    code: str
    two_fa_token: str
    fingerprint: str


class ConfirmTwoFaCodeHandler(BaseHandler[ConfirmTwoFaCodeQuery, dtos.TokensExpire]):
    async def handle(
        self, query: ConfirmTwoFaCodeQuery, **kwargs: Any
    ) -> dtos.TokensExpire:
        raise ServiceNotImplementedError(
            "Two-factor authentication requires its own storage model"
        )
