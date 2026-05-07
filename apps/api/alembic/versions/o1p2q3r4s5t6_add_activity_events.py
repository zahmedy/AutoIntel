"""add activity events

Revision ID: o1p2q3r4s5t6
Revises: n0o1p2q3r4s5
Create Date: 2026-05-07 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "o1p2q3r4s5t6"
down_revision = "n0o1p2q3r4s5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activityevent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("session_id", sa.String(length=80), nullable=True),
        sa.Column("car_id", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=80), nullable=True),
        sa.Column("path", sa.String(length=512), nullable=True),
        sa.Column("search_query", sa.String(length=256), nullable=True),
        sa.Column("filters_json", sa.String(), nullable=True),
        sa.Column("metadata_json", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["car_id"], ["carlisting.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_activityevent_car_id"), "activityevent", ["car_id"], unique=False)
    op.create_index(op.f("ix_activityevent_created_at"), "activityevent", ["created_at"], unique=False)
    op.create_index(op.f("ix_activityevent_event_type"), "activityevent", ["event_type"], unique=False)
    op.create_index(op.f("ix_activityevent_search_query"), "activityevent", ["search_query"], unique=False)
    op.create_index(op.f("ix_activityevent_session_id"), "activityevent", ["session_id"], unique=False)
    op.create_index(op.f("ix_activityevent_source"), "activityevent", ["source"], unique=False)
    op.create_index(op.f("ix_activityevent_user_id"), "activityevent", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_activityevent_user_id"), table_name="activityevent")
    op.drop_index(op.f("ix_activityevent_source"), table_name="activityevent")
    op.drop_index(op.f("ix_activityevent_session_id"), table_name="activityevent")
    op.drop_index(op.f("ix_activityevent_search_query"), table_name="activityevent")
    op.drop_index(op.f("ix_activityevent_event_type"), table_name="activityevent")
    op.drop_index(op.f("ix_activityevent_created_at"), table_name="activityevent")
    op.drop_index(op.f("ix_activityevent_car_id"), table_name="activityevent")
    op.drop_table("activityevent")
