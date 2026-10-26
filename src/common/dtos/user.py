from __future__ import annotations

from typing import Annotated
from uuid import UUID

from pydantic import EmailStr, Field

from src.common.dtos.base import DTO
from src.common.dtos.role import Role
from src.database.models.types import RoleType

PasswordStr = Annotated[
    str,
    Field(
        description="Password must contain at least 8 characters and be less than 128 characters",
        min_length=8,
        max_length=127,
    ),
]

LoginStr = Annotated[
    EmailStr,
    Field(
        description="Login must be valid email and be less than 128 characters",
        max_length=127,
        examples=["admin@example.com"],
    ),
]


class PublicUser(DTO):
    uuid: UUID
    login: LoginStr | None = None
    active: bool
    subscription_auto_renewal: bool

    # relations
    roles: list[Role] | None = None


class PrivateUser(PublicUser):
    password: PasswordStr

    # Permission data
    refresh_token: str | None = None
    access_token: str | None = None


class Users(DTO):
    data: list[PublicUser]
    total: int
    offset: int
    limit: int


class CreateUser(DTO):
    login: LoginStr
    password: PasswordStr
    roles: set[RoleType]


class UpdateUser(DTO):
    login: LoginStr | None = None
    password: PasswordStr | None = None
    subscription_auto_renewal: bool | None = None


class UpdateAdminUser(UpdateUser):
    active: bool | None = None


class UpdateUserRole(DTO):
    roles: set[RoleType] | None = None


class Fingerprint(DTO):
    fingerprint: str


class UserLogin(Fingerprint):
    login: LoginStr
    password: PasswordStr


class RegisterUser(DTO):
    login: LoginStr
    password: PasswordStr


class SelectManyUsers(DTO):
    login: str | None = None
    active: bool | None = None
    offset: int = 0
    limit: int = 10


class ResetPassword(DTO):
    login: LoginStr


class ConfirmResetPassword(Fingerprint):
    password: PasswordStr


class ResendCode(DTO):
    login: LoginStr
