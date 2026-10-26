from typing import Required, TypedDict


class CreateUserType(TypedDict):
    login: str | None
    password: Required[str]


class UpdateUserType(TypedDict, total=False):
    login: str | None
    password: str | None
    active: bool | None
    subscription_auto_renewal: bool | None
