import json
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models.car import CarListing
from app.models.vehicle_intelligence import PricePredictionRecord, VinDecodeRecord
from app.models.user import User
from app.schemas.car import PricePredictionRequest


def _json_dumps(payload: Any) -> str:
    return json.dumps(payload, default=str, sort_keys=True)


def _vin_decode_for_update(
    session: Session,
    user: User,
    vin_decode_id: int | None = None,
    car_id: int | None = None,
) -> VinDecodeRecord | None:
    if vin_decode_id is not None:
        return session.exec(
            select(VinDecodeRecord).where(
                VinDecodeRecord.id == vin_decode_id,
                VinDecodeRecord.user_id == user.id,
            )
        ).first()

    if car_id is not None:
        return session.exec(
            select(VinDecodeRecord)
            .where(VinDecodeRecord.car_id == car_id, VinDecodeRecord.user_id == user.id)
            .order_by(VinDecodeRecord.updated_at.desc(), VinDecodeRecord.id.desc())
        ).first()

    return None


def _price_prediction_for_update(
    session: Session,
    user: User,
    price_prediction_id: int | None = None,
    car_id: int | None = None,
) -> PricePredictionRecord | None:
    if price_prediction_id is not None:
        return session.exec(
            select(PricePredictionRecord).where(
                PricePredictionRecord.id == price_prediction_id,
                PricePredictionRecord.user_id == user.id,
            )
        ).first()

    if car_id is not None:
        return session.exec(
            select(PricePredictionRecord)
            .where(PricePredictionRecord.car_id == car_id, PricePredictionRecord.user_id == user.id)
            .order_by(PricePredictionRecord.updated_at.desc(), PricePredictionRecord.id.desc())
        ).first()

    return None


def record_vin_decode_data(
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
    vin_decode_id: int | None = None,
) -> VinDecodeRecord:
    now = datetime.utcnow()
    record = _vin_decode_for_update(session, user, vin_decode_id, car_id)
    if record is None:
        record = VinDecodeRecord(user_id=user.id or 0, created_at=now)

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


def record_price_prediction_data(
    session: Session,
    *,
    user: User,
    payload: PricePredictionRequest,
    price_prediction: int,
    model_name: str | None = None,
    model_version: str | None = None,
    raw_payload: Any = None,
) -> PricePredictionRecord:
    now = datetime.utcnow()
    record = _price_prediction_for_update(session, user, payload.price_prediction_id, payload.car_id)
    if record is None:
        record = PricePredictionRecord(user_id=user.id or 0, car_id=payload.car_id, created_at=now)

    record.car_id = payload.car_id or record.car_id
    record.price_prediction = price_prediction
    record.price_model_name = model_name
    record.price_model_version = model_version
    record.price_prediction_created_at = now
    record.prediction_payload_json = _json_dumps(payload.model_dump())
    record.price_prediction_raw_json = _json_dumps(raw_payload) if raw_payload is not None else None
    record.updated_at = now

    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def attach_vehicle_intelligence_records_to_listing(
    session: Session,
    *,
    user: User,
    car: CarListing,
    vin_decode_id: int | None = None,
    price_prediction_id: int | None = None,
) -> None:
    if car.id is None:
        return

    now = datetime.utcnow()

    if vin_decode_id is not None:
        vin_decode = _vin_decode_for_update(session, user, vin_decode_id)
        if vin_decode is not None:
            vin_decode.car_id = car.id
            vin_decode.updated_at = now
            session.add(vin_decode)

    if price_prediction_id is not None:
        price_prediction = _price_prediction_for_update(session, user, price_prediction_id)
        if price_prediction is not None:
            price_prediction.car_id = car.id
            price_prediction.updated_at = now
            session.add(price_prediction)
