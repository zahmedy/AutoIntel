"""add email verification codes

Revision ID: p2q3r4s5t6u7
Revises: o1p2q3r4s5t6
Create Date: 2026-05-08 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "p2q3r4s5t6u7"
down_revision = "o1p2q3r4s5t6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "emailverificationcode",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.String(length=64), nullable=False),
        sa.Column("code_hash", sa.String(length=128), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_emailverificationcode_attempts"), "emailverificationcode", ["attempts"], unique=False)
    op.create_index(op.f("ix_emailverificationcode_consumed_at"), "emailverificationcode", ["consumed_at"], unique=False)
    op.create_index(op.f("ix_emailverificationcode_created_at"), "emailverificationcode", ["created_at"], unique=False)
    op.create_index(op.f("ix_emailverificationcode_email"), "emailverificationcode", ["email"], unique=False)
    op.create_index(op.f("ix_emailverificationcode_expires_at"), "emailverificationcode", ["expires_at"], unique=False)
    op.create_index(op.f("ix_emailverificationcode_purpose"), "emailverificationcode", ["purpose"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_emailverificationcode_purpose"), table_name="emailverificationcode")
    op.drop_index(op.f("ix_emailverificationcode_expires_at"), table_name="emailverificationcode")
    op.drop_index(op.f("ix_emailverificationcode_email"), table_name="emailverificationcode")
    op.drop_index(op.f("ix_emailverificationcode_created_at"), table_name="emailverificationcode")
    op.drop_index(op.f("ix_emailverificationcode_consumed_at"), table_name="emailverificationcode")
    op.drop_index(op.f("ix_emailverificationcode_attempts"), table_name="emailverificationcode")
    op.drop_table("emailverificationcode")
