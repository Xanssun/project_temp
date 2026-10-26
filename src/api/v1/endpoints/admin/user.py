from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.common.responses import OkResponse
from src.api.v1 import handlers
from src.api.v1.auth import Authorization, InternalAuthorization
from src.common import dtos
from src.common.interfaces.mediator import MediatorProtocol
from src.database.models.types import RoleType, _UserLoadsType

user_router = APIRouter(prefix="/user", tags=["Admin | User"])


@user_router.post(
    "/bootstrap",
    status_code=status.HTTP_201_CREATED,
    response_model=dtos.PublicUser,
    dependencies=[Depends(InternalAuthorization())],
)
async def bootstrap_admin_endpoint(
    body: dtos.RegisterUser,
    mediator: Annotated[MediatorProtocol, Depends()],
) -> OkResponse[dtos.PublicUser]:
    return OkResponse(
        await mediator.send(
            handlers.user.CreateUserQuery(
                login=body.login,
                password=body.password,
                roles={RoleType.ADMIN},
            )
        ),
        status_code=status.HTTP_201_CREATED,
    )


@user_router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=dtos.PublicUser,
    dependencies=[Depends(Authorization("Admin"))],
)
async def create_user_endpoint(
    body: dtos.CreateUser,
    mediator: Annotated[MediatorProtocol, Depends()],
) -> OkResponse[dtos.PublicUser]:
    return OkResponse(
        await mediator.send(handlers.user.CreateUserQuery(**body.model_dump()))
    )


@user_router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=dtos.PublicUser,
    dependencies=[Depends(Authorization("Admin"))],
)
async def select_user_endpoint(
    user_id: UUID,
    mediator: Annotated[MediatorProtocol, Depends()],
    s: tuple[_UserLoadsType, ...] = Query(default=(), title="Additional relations"),
) -> OkResponse[dtos.PublicUser]:
    return OkResponse(
        await mediator.send(handlers.user.SelectUserQuery(loads=s, user_uuid=user_id))
    )


@user_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=dtos.Users,
    dependencies=[Depends(Authorization("Admin"))],
)
async def select_many_users_endpoint(
    query: Annotated[dtos.SelectManyUsers, Depends(dtos.SelectManyUsers)],
    mediator: Annotated[MediatorProtocol, Depends()],
    s: tuple[_UserLoadsType, ...] = Query(default=(), title="Additional relations"),
) -> OkResponse[dtos.Users]:
    return OkResponse(
        await mediator.send(
            handlers.user.SelectUsersQuery(loads=s, **query.model_dump())
        )
    )


@user_router.patch(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=dtos.PublicUser,
    dependencies=[Depends(Authorization("Admin"))],
)
async def update_user_endpoint(
    user_id: UUID,
    body: dtos.UpdateAdminUser,
    mediator: Annotated[MediatorProtocol, Depends()],
) -> OkResponse[dtos.PublicUser]:
    return OkResponse(
        await mediator.send(
            handlers.user.UpdateUserQuery(user_uuid=user_id, **body.model_dump())
        )
    )


@user_router.put(
    "/{user_id}/roles",
    status_code=status.HTTP_200_OK,
    response_model=dtos.PublicUser,
    dependencies=[Depends(Authorization("Admin"))],
)
async def update_user_roles_endpoint(
    user_id: UUID,
    body: dtos.UpdateUserRole,
    mediator: Annotated[MediatorProtocol, Depends()],
) -> OkResponse[dtos.PublicUser]:
    return OkResponse(
        await mediator.send(
            handlers.user.UpdateUserQuery(user_uuid=user_id, **body.model_dump())
        )
    )


@user_router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=dtos.PublicUser,
    dependencies=[Depends(Authorization("Admin"))],
)
async def delete_user_endpoint(
    user_id: UUID,
    mediator: Annotated[MediatorProtocol, Depends()],
) -> OkResponse[dtos.PublicUser]:
    return OkResponse(
        await mediator.send(handlers.user.DeleteUserQuery(user_uuid=user_id))
    )
