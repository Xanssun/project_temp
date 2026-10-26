"""Seed default roles.

Revision ID: 02_seed_default_roles
Revises: 01_509924a108b4
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "02_seed_default_roles"
down_revision: str | None = "01_509924a108b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    role = sa.table("role", sa.column("name", sa.String()))
    op.bulk_insert(role, [{"name": "Admin"}, {"name": "User"}])


def downgrade() -> None:
    op.execute(
        sa.text(
            'DELETE FROM user_role WHERE role_uuid IN '
            "(SELECT uuid FROM role WHERE name IN ('Admin', 'User'))"
        )
    )
    op.execute(sa.text("DELETE FROM role WHERE name IN ('Admin', 'User')"))
