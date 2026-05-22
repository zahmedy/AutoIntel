"""split vehicle intelligence records

Revision ID: r4s5t6u7v8w9
Revises: q3r4s5t6u7v8
Create Date: 2026-05-21 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "r4s5t6u7v8w9"
down_revision = "q3r4s5t6u7v8"
branch_labels = None
depends_on = None


def _reset_sequence(table_name: str) -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(
        sa.text(
            f"""
            SELECT setval(
                pg_get_serial_sequence('{table_name}', 'id'),
                COALESCE((SELECT MAX(id) FROM {table_name}), 1),
                (SELECT COUNT(*) FROM {table_name}) > 0
            )
            """
        )
    )


def upgrade() -> None:
    op.create_table(
        "vin_decode",
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
        sa.Column("vin_decode_payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["car_id"], ["carlisting.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vin_decode_car_id"), "vin_decode", ["car_id"], unique=False)
    op.create_index(op.f("ix_vin_decode_corrected_vin"), "vin_decode", ["corrected_vin"], unique=False)
    op.create_index(op.f("ix_vin_decode_created_at"), "vin_decode", ["created_at"], unique=False)
    op.create_index(op.f("ix_vin_decode_decoded_make"), "vin_decode", ["decoded_make"], unique=False)
    op.create_index(op.f("ix_vin_decode_decoded_model"), "vin_decode", ["decoded_model"], unique=False)
    op.create_index(op.f("ix_vin_decode_decoded_year"), "vin_decode", ["decoded_year"], unique=False)
    op.create_index(op.f("ix_vin_decode_detected_vin"), "vin_decode", ["detected_vin"], unique=False)
    op.create_index(op.f("ix_vin_decode_model_confidence"), "vin_decode", ["model_confidence"], unique=False)
    op.create_index(op.f("ix_vin_decode_updated_at"), "vin_decode", ["updated_at"], unique=False)
    op.create_index(op.f("ix_vin_decode_user_id"), "vin_decode", ["user_id"], unique=False)

    op.create_table(
        "price_prediction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("car_id", sa.Integer(), nullable=True),
        sa.Column("price_prediction", sa.Integer(), nullable=True),
        sa.Column("price_model_name", sa.String(), nullable=True),
        sa.Column("price_model_version", sa.String(), nullable=True),
        sa.Column("price_prediction_created_at", sa.DateTime(), nullable=True),
        sa.Column("prediction_payload_json", sa.Text(), nullable=True),
        sa.Column("price_prediction_raw_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["car_id"], ["carlisting.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_price_prediction_car_id"), "price_prediction", ["car_id"], unique=False)
    op.create_index(op.f("ix_price_prediction_created_at"), "price_prediction", ["created_at"], unique=False)
    op.create_index(op.f("ix_price_prediction_price_model_name"), "price_prediction", ["price_model_name"], unique=False)
    op.create_index(op.f("ix_price_prediction_price_model_version"), "price_prediction", ["price_model_version"], unique=False)
    op.create_index(op.f("ix_price_prediction_price_prediction"), "price_prediction", ["price_prediction"], unique=False)
    op.create_index(
        op.f("ix_price_prediction_price_prediction_created_at"),
        "price_prediction",
        ["price_prediction_created_at"],
        unique=False,
    )
    op.create_index(op.f("ix_price_prediction_updated_at"), "price_prediction", ["updated_at"], unique=False)
    op.create_index(op.f("ix_price_prediction_user_id"), "price_prediction", ["user_id"], unique=False)

    op.execute(
        sa.text(
            """
            INSERT INTO vin_decode (
                id,
                user_id,
                car_id,
                vin_image_content_type,
                vin_image_bytes,
                detected_vin,
                corrected_vin,
                model_confidence,
                decoded_make,
                decoded_model,
                decoded_year,
                vin_decode_payload_json,
                created_at,
                updated_at
            )
            SELECT
                id,
                user_id,
                car_id,
                vin_image_content_type,
                vin_image_bytes,
                detected_vin,
                corrected_vin,
                model_confidence,
                decoded_make,
                decoded_model,
                decoded_year,
                vin_decode_payload_json,
                created_at,
                updated_at
            FROM mltrainingrecord
            WHERE detected_vin IS NOT NULL
                OR corrected_vin IS NOT NULL
                OR vin_image_bytes IS NOT NULL
                OR decoded_make IS NOT NULL
                OR decoded_model IS NOT NULL
                OR decoded_year IS NOT NULL
                OR vin_decode_payload_json IS NOT NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO price_prediction (
                id,
                user_id,
                car_id,
                price_prediction,
                price_model_name,
                price_model_version,
                price_prediction_created_at,
                prediction_payload_json,
                price_prediction_raw_json,
                created_at,
                updated_at
            )
            SELECT
                id,
                user_id,
                car_id,
                price_prediction,
                price_model_name,
                price_model_version,
                price_prediction_created_at,
                prediction_payload_json,
                price_prediction_raw_json,
                created_at,
                updated_at
            FROM mltrainingrecord
            WHERE price_prediction IS NOT NULL
                OR price_model_name IS NOT NULL
                OR price_model_version IS NOT NULL
                OR price_prediction_created_at IS NOT NULL
                OR prediction_payload_json IS NOT NULL
                OR price_prediction_raw_json IS NOT NULL
            """
        )
    )
    _reset_sequence("vin_decode")
    _reset_sequence("price_prediction")

    op.drop_table("mltrainingrecord")


def downgrade() -> None:
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
        sa.Column("price_model_name", sa.String(), nullable=True),
        sa.Column("price_model_version", sa.String(), nullable=True),
        sa.Column("price_prediction_created_at", sa.DateTime(), nullable=True),
        sa.Column("final_listed_price", sa.Integer(), nullable=True),
        sa.Column("edited_listed_price", sa.Integer(), nullable=True),
        sa.Column("car_sold", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("final_sold_price", sa.Integer(), nullable=True),
        sa.Column("days_on_market", sa.Integer(), nullable=True),
        sa.Column("prediction_payload_json", sa.Text(), nullable=True),
        sa.Column("price_prediction_raw_json", sa.Text(), nullable=True),
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
    op.create_index(op.f("ix_mltrainingrecord_price_model_name"), "mltrainingrecord", ["price_model_name"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_price_model_version"), "mltrainingrecord", ["price_model_version"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_price_prediction"), "mltrainingrecord", ["price_prediction"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_price_prediction_created_at"), "mltrainingrecord", ["price_prediction_created_at"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_updated_at"), "mltrainingrecord", ["updated_at"], unique=False)
    op.create_index(op.f("ix_mltrainingrecord_user_id"), "mltrainingrecord", ["user_id"], unique=False)

    op.execute(
        sa.text(
            """
            INSERT INTO mltrainingrecord (
                id,
                user_id,
                car_id,
                vin_image_content_type,
                vin_image_bytes,
                detected_vin,
                corrected_vin,
                model_confidence,
                decoded_make,
                decoded_model,
                decoded_year,
                price_prediction,
                price_model_name,
                price_model_version,
                price_prediction_created_at,
                prediction_payload_json,
                price_prediction_raw_json,
                vin_decode_payload_json,
                created_at,
                updated_at
            )
            SELECT
                COALESCE(v.id, p.id),
                COALESCE(v.user_id, p.user_id),
                COALESCE(v.car_id, p.car_id),
                v.vin_image_content_type,
                v.vin_image_bytes,
                v.detected_vin,
                v.corrected_vin,
                v.model_confidence,
                v.decoded_make,
                v.decoded_model,
                v.decoded_year,
                p.price_prediction,
                p.price_model_name,
                p.price_model_version,
                p.price_prediction_created_at,
                p.prediction_payload_json,
                p.price_prediction_raw_json,
                v.vin_decode_payload_json,
                COALESCE(v.created_at, p.created_at),
                COALESCE(v.updated_at, p.updated_at)
            FROM vin_decode v
            FULL OUTER JOIN price_prediction p ON p.id = v.id
            """
        )
    )
    _reset_sequence("mltrainingrecord")

    op.drop_table("price_prediction")
    op.drop_table("vin_decode")
