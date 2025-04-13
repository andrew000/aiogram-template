"""
Initial.

Revision ID: 000000000000
Revises:
Create Date: 2025-04-13 19:51:58.981199+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "000000000000"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "chats",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("chat_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), server_default=sa.text("NULL"), nullable=True),
        sa.Column("username", postgresql.CITEXT(), server_default=sa.text("NULL"), nullable=True),
        sa.Column(
            "registration_datetime",
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'UTC'::text)"),
            nullable=False,
        ),
        sa.Column("migrate_from_chat_id", sa.BigInteger(), server_default=sa.text("NULL"), nullable=True),
        sa.Column("migrate_datetime", sa.DateTime(), server_default=sa.text("NULL"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("username", postgresql.CITEXT(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), server_default=sa.text("NULL"), nullable=True),
        sa.Column(
            "registration_datetime",
            postgresql.TIMESTAMP(precision=0),
            server_default=sa.text("(now() AT TIME ZONE 'UTC'::text)"),
            nullable=False,
        ),
        sa.Column("pm_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_table(
        "chats_settings",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("language_code", sa.String(length=2), server_default=sa.text("'en'"), nullable=False),
        sa.Column("timezone", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["id"], ["chats.id"], onupdate="CASCADE", deferrable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users_settings",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("language_code", sa.String(length=2), server_default=sa.text("'en'"), nullable=False),
        sa.Column("gender", sa.String(length=1), server_default=sa.text("'m'"), nullable=False),
        sa.Column("is_banned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.ForeignKeyConstraint(["id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users_settings")
    op.drop_table("chats_settings")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
    op.drop_table("chats")
    # ### end Alembic commands ###
