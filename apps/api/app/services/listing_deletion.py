import logging

from sqlalchemy import delete
from sqlmodel import Session, select

from app.models.activity import ActivityEvent
from app.models.car import CarListing, CarMedia, SavedCar
from app.models.chat import ChatMessage
from app.models.lead import Lead
from app.models.notification import Notification
from app.models.report import UserReport
from app.models.vehicle_intelligence import PricePredictionRecord, VinDecodeRecord
from app.services.s3 import delete_object


logger = logging.getLogger("uvicorn.error")


def permanently_delete_listing(session: Session, car: CarListing) -> int:
    car_id = car.id
    if car_id is None:
        raise ValueError("Listing must be persisted before it can be deleted")

    media_items = session.exec(select(CarMedia).where(CarMedia.car_id == car_id)).all()
    storage_keys = [media.storage_key for media in media_items]

    # Reports reference both listings and offers, so remove them before leads.
    for model in (
        UserReport,
        Notification,
        ActivityEvent,
        ChatMessage,
        SavedCar,
        VinDecodeRecord,
        PricePredictionRecord,
        CarMedia,
        Lead,
    ):
        session.exec(delete(model).where(model.car_id == car_id))

    session.delete(car)
    session.commit()

    deleted_objects = 0
    for storage_key in storage_keys:
        try:
            delete_object(storage_key)
            deleted_objects += 1
        except Exception:
            logger.exception("Failed to delete storage object %s for listing %s", storage_key, car_id)

    return deleted_objects
