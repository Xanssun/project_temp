from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.api.common.responses import OkResponse
from src.api.v1 import handlers
from src.api.v1.auth import Authorization
from src.common import dtos
from src.common.interfaces.mediator import MediatorProtocol
from src.database.models.types import (
    _UserLoadsType,
)

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=dtos.PublicUser,
)
async def select_user_endpoint(
    user: Annotated[dtos.PrivateUser, Depends(Authorization())],
    mediator: Annotated[MediatorProtocol, Depends()],
    s: tuple[_UserLoadsType, ...] = Query(default=(), title="Additional relations"),
) -> OkResponse[dtos.PublicUser]:
    return OkResponse(
        await mediator.send(handlers.user.SelectUserQuery(loads=s, user_uuid=user.uuid))
    )


@user_router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=dtos.PublicUser,
)
async def update_user_endpoint(
    user: Annotated[dtos.PrivateUser, Depends(Authorization())],
    body: dtos.UpdateUser,
    mediator: Annotated[MediatorProtocol, Depends()],
) -> OkResponse[dtos.PublicUser]:
    return OkResponse(
        await mediator.send(
            handlers.user.UpdateUserQuery(user_uuid=user.uuid, **body.model_dump())
        )
    )


@user_router.delete(
    "",
    status_code=status.HTTP_200_OK,
    response_model=dtos.PublicUser,
)
async def delete_user_endpoint(
    user: Annotated[dtos.PrivateUser, Depends(Authorization())],
    mediator: Annotated[MediatorProtocol, Depends()],
) -> OkResponse[dtos.PublicUser]:
    return OkResponse(
        await mediator.send(handlers.user.DeleteUserQuery(user_uuid=user.uuid))
    )
