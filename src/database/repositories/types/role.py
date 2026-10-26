from typing import Required, TypedDict

from src.database.models.types import RoleType


class CreateRoleType(TypedDict):
    name: Required[RoleType]


class UpdateRoleType(TypedDict, total=False):
    name: RoleType | None
