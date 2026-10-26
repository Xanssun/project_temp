from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.api.common.docs import (
    ForbiddenError,
    NotFoundError,
    UnAuthorizedError,
)
from src.api.common.responses import OkResponse
from src.api.v1.auth import Authorization
from src.api.v1.handlers import auth
from src.common import dtos
from src.common.interfaces.mediator import MediatorProtocol
from src.common.stub import Stub
from src.core.settings import Settings

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    "/register",
    status_code=status.HTTP_200_OK,
    response_model=dtos.Status,
)
async def register_endpoint(
    body: dtos.RegisterUser,
    mediator: Annotated[MediatorProtocol, Depends()],
) -> OkResponse[dtos.Status]:
    return OkResponse(
        await mediator.send(auth.RegisterUserQuery(**body.model_dump()))
    )


@auth_router.post(
    "/login",
    response_model=dtos.Token,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": NotFoundError},
        status.HTTP_401_UNAUTHORIZED: {"model": UnAuthorizedError},
        status.HTTP_403_FORBIDDEN: {"model": ForbiddenError},
    },
)
async def login_endpoint(
    body: dtos.UserLogin,
    mediator: Annotated[MediatorProtocol, Depends()],
    settings: Annotated[Settings, Depends(Stub(Settings))],  # type: ignore
) -> OkResponse[dtos.Token]:
    result: dtos.TokensExpire = await mediator.send(
        auth.LoginQuery(
            login=body.login,
            password=body.password,
            fingerprint=body.fingerprint,
        )
    )
    response = OkResponse(dtos.Token(token=result.tokens.access))
    response.set_cookie(
        "refresh_token",
        value=result.tokens.refresh,
        expires=result.refresh_expire,
        httponly=True,
        secure=settings.server.production,
        samesite="lax",
    )
    return response


@auth_router.post(
    "/refresh",
    response_model=dtos.Token,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": UnAuthorizedError},
        status.HTTP_403_FORBIDDEN: {"model": ForbiddenError},
    },
)
async def refresh_endpoint(
    body: dtos.Fingerprint,
    mediator: Annotated[MediatorProtocol, Depends()],
    settings: Annotated[Settings, Depends(Stub(Settings))],  # type: ignore
    user: Annotated[dtos.PrivateUser, Depends(Authorization(only_refresh=True))],
) -> OkResponse[dtos.Token]:
    result = await mediator.send(auth.RefresTokenQuery(data=body, user=user))
    response = OkResponse(dtos.Token(token=result.tokens.access))
    response.set_cookie(
        "refresh_token",
        value=result.tokens.refresh,
        expires=result.refresh_expire,
        httponly=True,
        secure=settings.server.production,
        samesite="lax",
    )

    return response


@auth_router.post(
    "/logout",
    response_model=dtos.Status,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": UnAuthorizedError},
        status.HTTP_403_FORBIDDEN: {"model": ForbiddenError},
    },
)
async def logout_endpoint(
    mediator: Annotated[MediatorProtocol, Depends()],
    user: Annotated[dtos.PrivateUser, Depends(Authorization())],
) -> OkResponse[dtos.Status]:
    result = await mediator.send(auth.LogoutQuery(user=user))
    response = OkResponse(result)
    response.delete_cookie("refresh_token")

    return response


