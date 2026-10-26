from typing import Required, TypedDict
from uuid import UUID


class CreateUserRoleType(TypedDict):
    user_uuid: Required[UUID]
    role_uuid: Required[UUID]
