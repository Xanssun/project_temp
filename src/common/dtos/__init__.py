from __future__ import annotations

import importlib

from .auth_token import (
    ConfrimTwoFa,
    SetupTwoFa,
    Token,
    Tokens,
    TokensExpire,
    TwoFaToken,
)
from .base import DTO
from .role import CreateRole, Role, Roles, SelectManyRoles, UpdateRole
from .status import Status
from .user import (
    ConfirmResetPassword,
    CreateUser,
    Fingerprint,
    PrivateUser,
    PublicUser,
    RegisterUser,
    ResendCode,
    ResetPassword,
    SelectManyUsers,
    UpdateAdminUser,
    UpdateUser,
    UpdateUserRole,
    UserLogin,
    Users,
)
from .user_role import UserRole, UserRoles

__all__ = (
    "Token",
    "Tokens",
    "TokensExpire",
    "Status",
    "TwoFaToken",
    "ConfrimTwoFa",
    "SetupTwoFa",
    "Role",
    "Roles",
    "SelectManyRoles",
    "CreateRole",
    "UpdateRole",
    "PublicUser",
    "PrivateUser",
    "Users",
    "CreateUser",
    "UpdateUser",
    "UpdateAdminUser",
    "UpdateUserRole",
    "Fingerprint",
    "UserLogin",
    "RegisterUser",
    "SelectManyUsers",
    "ResetPassword",
    "ConfirmResetPassword",
    "ResendCode",
    "UserRole",
    "UserRoles",
)


def rebuild_models() -> None:
    module = importlib.import_module(__name__)
    ns = module.__dict__

    for model_name in set(__all__):
        model = getattr(module, model_name, None)
        if model and issubclass(model, DTO):
            model.model_rebuild(_types_namespace=ns)


rebuild_models()
