"""add ml training records

Revision ID: q3r4s5t6u7v8
Revises: p2q3r4s5t6u7
Create Date: 2026-05-17 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "q3r4s5t6u7v8"
down_revision = "p2q3r4s5t6u7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mltrainingrecord",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("car_id", sa.Integer(), nullable=True),
        sa.Column("vin_image_content_type", sa.String(), nullable=True),
        sa.Column("vin_image_bytes", sa.LargeBinary(), nullable=True),
        sa.Column("detected_vin", sa.String(), nullable=True),
        sa.Column("corrected_vin", sa.String(), nullable=True),
        sa.Column("model_confidence", sa.Float(), nullable=True),
        sa.Column("decoded_make", sa.String(), nullable=True),
        sa.Column("decoded_model", sa.String(), nullable=True),
        sa.Column("decoded_year", sa.Integer(), nullable=True),
        sa.Column("price_prediction", sa.Integer(), nullable=True),
        sa.Column("final_listed_price", sa.Integer(), nullable=True),
        sa.Column("edited_listed_price", sa.Integer(), nullable=True),
        sa.Column("car_sold", sa.Boolean(), nullable=False),
        sa.Column("final_sold_price", sa.Integer(), nullable=True),
        sa.Column("days_on_market", sa.Integer(), nullable=True),
        sa.Column("prediction_payload_json", sa.Text(), nullable=True),
        sa.Column("vin_decode_payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["car_id"], ["carlisting.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mltrainingrecord_car_id"), "mltrainingrecord", ["car_id"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_car_sold"), "mltrainingrecord", ["car_sold"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_corrected_vin"), "mltrainingrecord", ["corrected_vin"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_created_at"), "mltrainingrecord", ["created_at"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_days_on_market"), "mltrainingrecord", ["days_on_market"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_decoded_make"), "mltrainingrecord", ["decoded_make"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_decoded_model"), "mltrainingrecord", ["decoded_model"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_decoded_year"), "mltrainingrecord", ["decoded_year"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_detected_vin"), "mltrainingrecord", ["detected_vin"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_edited_listed_price"), "mltrainingrecord", ["edited_listed_price"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_final_listed_price"), "mltrainingrecord", ["final_listed_price"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_final_sold_price"), "mltrainingrecord", ["final_sold_price"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_model_confidence"), "mltrainingrecord", ["model_confidence"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_price_prediction"), "mltrainingrecord", ["price_prediction"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_updated_at"), "mltrainingrecord", ["updated_at"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_user_id"), "mltrainingrecord", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_mltrainingrecord_user_id"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_updated_at"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_price_prediction"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_model_confidence"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_final_sold_price"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_final_listed_price"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_edited_listed_price"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_detected_vin"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_decoded_year"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_decoded_model"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_decoded_make"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_days_on_market"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_created_at"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_corrected_vin"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_car_sold"), table_name="mltrainingrecord")
    op.drop_index(op.f("ix_mltrainingrecord_car_id"), table_name="mltrainingrecord")
    op.drop_table("mltrainingrecord")
