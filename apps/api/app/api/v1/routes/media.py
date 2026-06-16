from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.models.car import CarListing, CarMedia
from app.schemas.media import PresignRequest, PresignResponse, MediaCompleteRequest
from app.services.s3 import (
    delete_object,
    is_storage_key_for_car,
    make_storage_key,
    presign_put,
    public_url_for_key,
)

router = APIRouter(tags=["media"])

def ensure_owner(car: CarListing, user: User):
    if car.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your listing")


def normalize_car_media(session: Session, car_id: int, cover_media_id: int | None = None) -> None:
    media_items = session.exec(
        select(CarMedia)
        .where(CarMedia.car_id == car_id)
        .order_by(CarMedia.sort_order.asc(), CarMedia.id.asc())
    ).all()

    if cover_media_id is not None:
        prioritized = [media for media in media_items if media.id == cover_media_id]
        remaining = [media for media in media_items if media.id != cover_media_id]
        media_items = prioritized + remaining

    cover_found = False
    for index, media in enumerate(media_items):
        media.sort_order = index
        should_be_cover = False
        if not cover_found and (media.is_cover or index == 0):
            should_be_cover = True
            cover_found = True
        media.is_cover = should_be_cover
        session.add(media)


@router.post("/cars/{car_id}/media/presign", response_model=PresignResponse)
def presign_upload(
    car_id: int,
    payload: PresignRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    car = session.exec(select(CarListing).where(CarListing.id == car_id)).first()
    if not car:
        raise HTTPException(status_code=404, detail="Not found")
    ensure_owner(car, user)

    storage_key = make_storage_key(car_id, payload.filename)
    upload_url = presign_put(storage_key, payload.content_type)
    public_url = public_url_for_key(storage_key)
    return PresignResponse(upload_url=upload_url, storage_key=storage_key, public_url=public_url)

@router.post("/cars/{car_id}/media/complete")
def complete_upload(
    car_id: int,
    payload: MediaCompleteRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    car = session.exec(select(CarListing).where(CarListing.id == car_id)).first()
    if not car:
        raise HTTPException(status_code=404, detail="Not found")
    ensure_owner(car, user)
    if not is_storage_key_for_car(payload.storage_key, car_id):
        raise HTTPException(status_code=400, detail="Invalid photo storage key")

    # sqlmodel may return a scalar int or a row-like object depending on backend/version.
    count_result = session.exec(
        select(func.count()).select_from(CarMedia).where(CarMedia.car_id == car_id)
    ).one()
    try:
        sort_order = int(count_result)
    except (TypeError, ValueError):
        sort_order = int(count_result[0])

    media = CarMedia(
        car_id=car_id,
        storage_key=payload.storage_key,
        public_url=public_url_for_key(payload.storage_key),
        sort_order=sort_order,
        is_cover=payload.is_cover,
    )
    session.add(media)
    session.commit()
    session.refresh(media)
    session.refresh(car)
    return {"ok": True, "media_id": media.id, "public_url": media.public_url}


@router.delete("/cars/{car_id}/media/{media_id}")
def delete_media(
    car_id: int,
    media_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    car = session.exec(select(CarListing).where(CarListing.id == car_id)).first()
    if not car:
        raise HTTPException(status_code=404, detail="Not found")
    ensure_owner(car, user)

    media = session.exec(
        select(CarMedia).where(CarMedia.id == media_id, CarMedia.car_id == car_id)
    ).first()
    if not media:
        raise HTTPException(status_code=404, detail="Photo not found")

    storage_key = media.storage_key
    session.delete(media)
    session.flush()
    normalize_car_media(session, car_id)
    session.commit()
    session.refresh(car)

    try:
        delete_object(storage_key)
    except Exception:
        pass

    return {"ok": True}


@router.post("/cars/{car_id}/media/{media_id}/main")
def set_main_media(
    car_id: int,
    media_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    car = session.exec(select(CarListing).where(CarListing.id == car_id)).first()
    if not car:
        raise HTTPException(status_code=404, detail="Not found")
    ensure_owner(car, user)

    media = session.exec(
        select(CarMedia).where(CarMedia.id == media_id, CarMedia.car_id == car_id)
    ).first()
    if not media:
        raise HTTPException(status_code=404, detail="Photo not found")

    normalize_car_media(session, car_id, cover_media_id=media_id)
    session.commit()
    session.refresh(car)

    return {"ok": True}
