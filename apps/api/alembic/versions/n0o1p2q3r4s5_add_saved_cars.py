"""add saved cars

Revision ID: n0o1p2q3r4s5
Revises: m9n0o1p2q3r4
Create Date: 2026-05-07 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "n0o1p2q3r4s5"
down_revision = "m9n0o1p2q3r4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "savedcar",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("car_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["car_id"], ["carlisting.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "car_id", name="uq_savedcar_user_car"),
    )
    op.create_index(op.f("ix_savedcar_car_id"), "savedcar", ["car_id"], unique=False)
    op.create_index(op.f("ix_savedcar_created_at"), "savedcar", ["created_at"], unique=False)
    op.create_index(op.f("ix_savedcar_user_id"), "savedcar", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_savedcar_user_id"), table_name="savedcar")
    op.drop_index(op.f("ix_savedcar_created_at"), table_name="savedcar")
    op.drop_index(op.f("ix_savedcar_car_id"), table_name="savedcar")
    op.drop_table("savedcar")
