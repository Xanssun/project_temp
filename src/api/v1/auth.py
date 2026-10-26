from collections import namedtuple
from typing import Annotated, cast

from fastapi import Depends, Header, Request
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param

from src.api.v1.handlers import auth
from src.common import dtos
from src.common.exceptions import ForbiddenError
from src.common.interfaces.mediator import MediatorProtocol
from src.common.stub import Stub
from src.core.settings import Settings
from src.database.models.types import PermissionType

Token = namedtuple("Token", ["access", "refresh"])


class InternalAuthorization(SecurityBase):
    def __init__(self) -> None:
        self.model = HTTPBearerModel()
        self.scheme_name = type(self).__name__

    async def __call__(
        self,
        internal_token: Annotated[str, Header(..., alias="X-Internal-Token")],
        settings: Annotated[Settings, Depends(Stub(Settings))], # type: ignore
    ) -> bool:
        expected_token = settings.server.internal_api_token

        if internal_token != expected_token:
            raise ForbiddenError("Invalid internal API token")

        return True


class Authorization(SecurityBase):
    def __init__(
        self,
        *permissions: PermissionType | None,
        excluded_permissions: list[PermissionType] | None = None,
        only_refresh: bool = False,
    ) -> None:
        """
        Initializes the Authorization class.

        Args:
            *permissions (PermissionType): type of role or roles, for instance Authorization("Admin", "Moderator") or Authorization("Admin")
            only_refresh (bool): Flag to indicate if the endpoint requires ONLY refresh token. Be cautious when using this flag.

        """
        self.model = HTTPBearerModel()
        self.scheme_name = type(self).__name__
        self._permission = permissions
        self._excluded_permissions = (
            tuple(excluded_permissions) if excluded_permissions else ()
        )
        self._only_refresh = only_refresh

    async def __call__(
        self, request: Request, mediator: Annotated[MediatorProtocol, Depends()]
    ) -> dtos.PrivateUser:
        token = self._get_tokens(request, self._only_refresh)

        result = await mediator.send(
            auth.PermissionQuery(
                excluede_permissions=self._excluded_permissions,
                permissions=self._permission,
                access_token=token.access,
                refresh_token=token.refresh,
            )
        )
        return cast(dtos.PrivateUser, result)

    def _get_tokens(self, request: Request, only_refresh: bool) -> Token:
        token = None
        refresh_token = request.cookies.get("refresh_token", "")
        if not only_refresh:
            access_token = request.headers.get("Authorization")
            scheme, token = get_authorization_scheme_param(access_token)

            if not (access_token and scheme and token):
                raise ForbiddenError("Not authenticated")
            if scheme.lower() != "bearer":
                raise ForbiddenError("Invalid authentication credentials")

        return Token(access=token, refresh=refresh_token)
