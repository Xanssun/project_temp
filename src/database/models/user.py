from typing import TYPE_CHECKING

from sqlalchemy import BOOLEAN, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Index

from src.database.models import Base
from src.database.models.base.mixins import ModelWithTimeMixin, ModelWithUUIDMixin

if TYPE_CHECKING:
    from src.database.models import (
        Role,
    )


class User(ModelWithUUIDMixin, ModelWithTimeMixin, Base):
    login: Mapped[str | None] = mapped_column(
        String, index=True, unique=True, nullable=True
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[bool] = mapped_column(BOOLEAN, default=True, nullable=False)

    subscription_auto_renewal: Mapped[bool] = mapped_column(
        BOOLEAN,
        default=True,
        server_default="true",
    )

    # relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_role",
        back_populates="users",
    )

    __table_args__ = (Index("idx_lower_login", func.lower(login), unique=True),)
