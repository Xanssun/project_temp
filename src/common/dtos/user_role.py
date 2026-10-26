from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.common.dtos.base import DTO


class UserRole(DTO):
    user_uuid: UUID
    role_uuid: UUID
    created_at: datetime
    updated_at: datetime


class UserRoles(DTO):
    data: list[UserRole]
    total: int
    offset: int | None = None
    limit: int | None = None
