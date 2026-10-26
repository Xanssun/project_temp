from enum import StrEnum
from typing import Literal

_UserLoadsType = Literal[
    "roles",
]
_RoleLoadsType = Literal["users",]

class RoleType(StrEnum):
    ADMIN = "Admin"
    USER = "User"


PermissionType = Literal[
    "Admin",
    "User",
]

EmailTemplateType = Literal[
    "REGISTRATION",
    "RECOVERY_PASSWORD",
]
