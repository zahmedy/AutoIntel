from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.core.deps import require_admin
from app.db.session import get_session
from app.models.car import CarListing, CarMedia, CarStatus
from app.models.user import User
from app.schemas.car import AdminCarListOut, AdminCarOut
from app.services.listing_deletion import permanently_delete_listing
from app.services.review import ADMIN_REVIEW_SOURCE, approve_listing, reject_listing

router = APIRouter(prefix="/admin", tags=["admin"])


def _owner_label(owner: User | None) -> str | None:
    if not owner:
        return None
    return f"@{owner.user_id}" if owner.user_id else owner.name or owner.email or owner.phone_e164


@router.get("/cars", response_model=AdminCarListOut)
def list_admin_cars(
    status: CarStatus | None = Query(default=None),
    q: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    filters = []
    if status is not None:
        filters.append(CarListing.status == status)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        filters.append(
            or_(
                CarListing.title.ilike(pattern),
                CarListing.make.ilike(pattern),
                CarListing.model.ilike(pattern),
                CarListing.city.ilike(pattern),
            )
        )

    count_statement = select(func.count()).select_from(CarListing)
    statement = select(CarListing)
    for condition in filters:
        count_statement = count_statement.where(condition)
        statement = statement.where(condition)

    total = int(session.exec(count_statement).one())
    cars = session.exec(
        statement.order_by(CarListing.created_at.desc(), CarListing.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    car_ids = [car.id for car in cars if car.id is not None]
    owner_ids = sorted({car.owner_id for car in cars})
    owners = {
        owner.id: owner
        for owner in session.exec(select(User).where(User.id.in_(owner_ids))).all()
        if owner.id is not None
    } if owner_ids else {}
    photo_counts = {
        car_id: count
        for car_id, count in session.exec(
            select(CarMedia.car_id, func.count(CarMedia.id))
            .where(CarMedia.car_id.in_(car_ids))
            .group_by(CarMedia.car_id)
        ).all()
    } if car_ids else {}

    return AdminCarListOut(
        page=page,
        page_size=page_size,
        total=total,
        items=[
            AdminCarOut(
                id=car.id or 0,
                status=car.status.value if isinstance(car.status, CarStatus) else str(car.status),
                owner_id=car.owner_id,
                owner_label=_owner_label(owners.get(car.owner_id)),
                title=car.title,
                make=car.make,
                model=car.model,
                year=car.year,
                city=car.city,
                price=car.price,
                photo_count=int(photo_counts.get(car.id or 0, 0)),
                created_at=car.created_at,
                published_at=car.published_at,
            )
            for car in cars
        ],
    )


@router.delete("/cars/{car_id}")
def delete_admin_car(
    car_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    car = session.get(CarListing, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Listing not found")

    deleted_objects = permanently_delete_listing(session, car)
    return {"ok": True, "deleted_car_id": car_id, "deleted_storage_objects": deleted_objects}


@router.post("/cars/{car_id}/approve")
def approve_car(
    car_id: int,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    car = session.exec(select(CarListing).where(CarListing.id == car_id)).first()
    if not car:
        raise HTTPException(status_code=404, detail="Not found")
    if car.status != CarStatus.pending_review:
        raise HTTPException(status_code=400, detail="Only pending_review can be approved")

    car = approve_listing(session, car, review_source=ADMIN_REVIEW_SOURCE)
    return {"ok": True, "status": car.status.value, "published_at": car.published_at}


@router.post("/cars/{car_id}/reject")
def reject_car(
    car_id: int,
    reason: str,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    car = session.exec(select(CarListing).where(CarListing.id == car_id)).first()
    if not car:
        raise HTTPException(status_code=404, detail="Not found")
    if car.status != CarStatus.pending_review:
        raise HTTPException(status_code=400, detail="Only pending_review can be rejected")

    car = reject_listing(session, car, review_source=ADMIN_REVIEW_SOURCE, review_reason=reason)
    return {"ok": True, "status": car.status.value, "reason": reason}
