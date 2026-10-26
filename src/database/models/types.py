from enum import StrEnum
from typing import Literal


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
