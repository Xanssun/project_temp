from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.common.responses import OkResponse
from src.api.v1 import handlers
from src.api.v1.auth import Authorization
from src.common import dtos
from src.common.interfaces.mediator import MediatorProtocol
from src.database.models.types import _RoleLoadsType

role_router = APIRouter(prefix="/roles", tags=["Admin | Role"])


@role_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=dtos.Role,
    dependencies=[Depends(Authorization("Admin"))],
)
async def create_role_endpoint(
    body: dtos.CreateRole,
    mediator: Annotated[MediatorProtocol, Depends()],
) -> OkResponse[dtos.Role]:
    return OkResponse(
        await mediator.send(handlers.role.CreateRoleQuery(**body.model_dump())),
        status_code=status.HTTP_201_CREATED,
    )


@role_router.get(
    "/{role_id}",
    status_code=status.HTTP_200_OK,
    response_model=dtos.Role,
    dependencies=[Depends(Authorization("Admin"))],
)
async def select_role_endpoint(
    role_id: UUID,
    mediator: Annotated[MediatorProtocol, Depends()],
    s: tuple[_RoleLoadsType, ...] = Query(default=(), title="Additional relations"),
) -> OkResponse[dtos.Role]:
    return OkResponse(
        await mediator.send(handlers.role.SelectRoleQuery(loads=s, role_uuid=role_id))
    )


@role_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=dtos.Roles,
    dependencies=[Depends(Authorization("Admin"))],
)
async def select_many_roles_endpoint(
    query: Annotated[dtos.SelectManyRoles, Depends(dtos.SelectManyRoles)],
    mediator: Annotated[MediatorProtocol, Depends()],
    s: tuple[_RoleLoadsType, ...] = Query(default=(), title="Additional relations"),
) -> OkResponse[dtos.Roles]:
    return OkResponse(
        await mediator.send(
            handlers.role.SelectManyRolesQuery(loads=s, **query.model_dump())
        )
    )


@role_router.patch(
    "/{role_id}",
    status_code=status.HTTP_200_OK,
    response_model=dtos.Role,
    dependencies=[Depends(Authorization("Admin"))],
)
async def update_role_endpoint(
    role_id: UUID,
    body: dtos.UpdateRole,
    mediator: Annotated[MediatorProtocol, Depends()],
) -> OkResponse[dtos.Role]:
    return OkResponse(
        await mediator.send(
            handlers.role.UpdateRoleQuery(
                role_uuid=role_id,
                **body.model_dump(exclude_none=True),
            )
        )
    )


@role_router.delete(
    "/{role_id}",
    status_code=status.HTTP_200_OK,
    response_model=dtos.Role,
    dependencies=[Depends(Authorization("Admin"))],
)
async def delete_role_endpoint(
    role_id: UUID,
    mediator: Annotated[MediatorProtocol, Depends()],
) -> OkResponse[dtos.Role]:
    return OkResponse(
        await mediator.send(handlers.role.DeleteRoleQuery(role_uuid=role_id))
    )
