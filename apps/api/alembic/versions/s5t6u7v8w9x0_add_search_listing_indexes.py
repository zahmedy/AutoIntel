"""add search listing indexes

Revision ID: s5t6u7v8w9x0
Revises: r4s5t6u7v8w9
Create Date: 2026-05-25 00:00:00.000000
"""

from alembic import op


revision = "s5t6u7v8w9x0"
down_revision = "r4s5t6u7v8w9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_carlisting_status_published_at_id", "carlisting", ["status", "published_at", "id"], unique=False)
    op.create_index("ix_carlisting_status_city_published_at", "carlisting", ["status", "city", "published_at"], unique=False)
    op.create_index("ix_carlisting_status_make_model_published_at", "carlisting", ["status", "make", "model", "published_at"], unique=False)
    op.create_index("ix_carlisting_status_price_published_at", "carlisting", ["status", "price", "published_at"], unique=False)
    op.create_index("ix_carlisting_status_mileage_published_at", "carlisting", ["status", "mileage", "published_at"], unique=False)
    op.create_index("ix_carlisting_status_year_published_at", "carlisting", ["status", "year", "published_at"], unique=False)
    op.create_index(
        "ix_carlisting_status_body_fuel_drivetrain",
        "carlisting",
        ["status", "body_type", "fuel_type", "drivetrain"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_carlisting_status_body_fuel_drivetrain", table_name="carlisting")
    op.drop_index("ix_carlisting_status_year_published_at", table_name="carlisting")
    op.drop_index("ix_carlisting_status_mileage_published_at", table_name="carlisting")
    op.drop_index("ix_carlisting_status_price_published_at", table_name="carlisting")
    op.drop_index("ix_carlisting_status_make_model_published_at", table_name="carlisting")
    op.drop_index("ix_carlisting_status_city_published_at", table_name="carlisting")
    op.drop_index("ix_carlisting_status_published_at_id", table_name="carlisting")
