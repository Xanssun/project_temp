import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database.models import Base
from src.database.models.base.mixins import ModelWithTimeMixin, ModelWithUUIDMixin

if TYPE_CHECKING:
    pass


class UserRole(ModelWithUUIDMixin, ModelWithTimeMixin, Base):
    user_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(True), ForeignKey("user.uuid", ondelete="CASCADE"), index=True
    )
    role_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(True), ForeignKey("role.uuid", ondelete="RESTRICT")
    )

    __table_args__ = (
        UniqueConstraint(
            "user_uuid",
            "role_uuid",
            name="uq_user_role",
        ),
    )
