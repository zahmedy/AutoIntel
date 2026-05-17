import json
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models.car import CarListing, CarStatus
from app.models.ml_training import MLTrainingRecord
from app.models.user import User
from app.schemas.car import PricePredictionRequest


def _json_dumps(payload: Any) -> str:
    return json.dumps(payload, default=str, sort_keys=True)


def _record_for_update(
    session: Session,
    user: User,
    training_record_id: int | None = None,
    car_id: int | None = None,
) -> MLTrainingRecord | None:
    if training_record_id is not None:
        return session.exec(
            select(MLTrainingRecord).where(
                MLTrainingRecord.id == training_record_id,
                MLTrainingRecord.user_id == user.id,
            )
        ).first()

    if car_id is not None:
        return session.exec(
            select(MLTrainingRecord)
            .where(MLTrainingRecord.car_id == car_id, MLTrainingRecord.user_id == user.id)
            .order_by(MLTrainingRecord.updated_at.desc(), MLTrainingRecord.id.desc())
        ).first()

    return None


def record_vin_scan_training_data(
    session: Session,
    *,
    user: User,
    image_bytes: bytes,
    content_type: str,
    detected_vin: str,
    corrected_vin: str | None,
    model_confidence: float | None,
    decoded: dict[str, Any],
    raw_decoded: dict[str, Any],
    car_id: int | None = None,
    training_record_id: int | None = None,
) -> MLTrainingRecord:
    now = datetime.utcnow()
    record = _record_for_update(session, user, training_record_id, car_id)
    if record is None:
        record = MLTrainingRecord(user_id=user.id or 0, created_at=now)

    record.car_id = car_id or record.car_id
    if image_bytes:
        record.vin_image_content_type = content_type
        record.vin_image_bytes = image_bytes
    if image_bytes or not record.detected_vin:
        record.detected_vin = detected_vin
    record.corrected_vin = corrected_vin or detected_vin
    record.model_confidence = model_confidence
    record.decoded_make = decoded.get("make") or record.decoded_make
    record.decoded_model = decoded.get("model") or record.decoded_model
    record.decoded_year = decoded.get("year") or record.decoded_year
    record.vin_decode_payload_json = _json_dumps(raw_decoded or decoded)
    record.updated_at = now

    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def record_price_prediction_training_data(
    session: Session,
    *,
    user: User,
    payload: PricePredictionRequest,
    price_prediction: int,
) -> MLTrainingRecord:
    now = datetime.utcnow()
    record = _record_for_update(session, user, payload.training_record_id, payload.car_id)
    if record is None:
        record = MLTrainingRecord(user_id=user.id or 0, car_id=payload.car_id, created_at=now)

    record.car_id = payload.car_id or record.car_id
    record.price_prediction = price_prediction
    record.prediction_payload_json = _json_dumps(payload.model_dump())
    record.updated_at = now

    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def sync_listing_training_data(
    session: Session,
    *,
    user: User,
    car: CarListing,
    training_record_id: int | None = None,
    previous_price: int | None = None,
) -> None:
    if car.id is None:
        return

    record = _record_for_update(session, user, training_record_id, car.id)
    if record is None:
        return

    now = datetime.utcnow()
    record.car_id = car.id
    if car.price is not None:
        if record.final_listed_price is None:
            record.final_listed_price = car.price
        if previous_price is not None and previous_price != car.price:
            record.edited_listed_price = car.price
        elif record.price_prediction is not None and car.price != record.price_prediction:
            record.edited_listed_price = car.price

    if car.status == CarStatus.sold:
        record.car_sold = True
        record.final_sold_price = car.sold_price
        if car.sold_at is not None:
            listed_at = car.published_at or car.created_at
            record.days_on_market = max((car.sold_at.date() - listed_at.date()).days, 0)

    record.updated_at = now
    session.add(record)
