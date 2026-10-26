from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from src.common.dtos.base import DTO
from src.database.models.types import RoleType

if TYPE_CHECKING:
    from src.common.dtos.user import PublicUser


class Role(DTO):
    uuid: UUID
    name: RoleType

    # relations
    users: list[PublicUser] | None = None


class Roles(DTO):
    data: list[Role]
    total: int
    offset: int
    limit: int = 10


class SelectManyRoles(DTO):
    name: RoleType | None = None
    offset: int = 0
    limit: int = 10


class CreateRole(DTO):
    name: RoleType


class UpdateRole(DTO):
    name: RoleType | None
