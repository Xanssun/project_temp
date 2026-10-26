from __future__ import annotations

import importlib

from .base import DTO
from .status import Status
from .token import Token, Tokens, TokensExpire

__all__ = (
    "Token",
    "Tokens",
    "TokensExpire",
    "Status",
)


def rebuild_models() -> None:
    module = importlib.import_module(__name__)
    ns = module.__dict__

    for model_name in set(__all__):
        model = getattr(module, model_name, None)
        if model and issubclass(model, DTO):
            model.model_rebuild(_types_namespace=ns)


rebuild_models()
