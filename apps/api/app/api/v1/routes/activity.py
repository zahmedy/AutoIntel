from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.deps import get_optional_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.activity import ActivityEventCreate, ActivityEventOut
from app.services.activity import log_activity_event

router = APIRouter(prefix="/activity", tags=["activity"])


@router.post("/events", response_model=ActivityEventOut)
def create_activity_event(
    payload: ActivityEventCreate,
    session: Session = Depends(get_session),
    user: User | None = Depends(get_optional_current_user),
):
    event = log_activity_event(
        session,
        event_type=payload.event_type,
        user=user,
        session_id=payload.session_id,
        car_id=payload.car_id,
        source=payload.source,
        path=payload.path,
        search_query=payload.search_query,
        filters=payload.filters,
        metadata=payload.metadata,
    )
    return ActivityEventOut(
        id=event.id or 0,
        event_type=event.event_type,
        user_id=event.user_id,
        session_id=event.session_id,
        car_id=event.car_id,
        source=event.source,
        path=event.path,
        search_query=event.search_query,
        created_at=event.created_at,
    )
