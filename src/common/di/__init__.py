from src.common.di.container import DynamicContainer, container

from .base import inject
from .marker import Depends

__all__ = (
    "DynamicContainer",
    "container",
    "Depends",
    "inject",
)
