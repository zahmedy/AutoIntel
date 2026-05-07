import json
from typing import Any

from sqlmodel import Session

from app.models.activity import ActivityEvent
from app.models.user import User


def _json_or_none(value: dict[str, Any] | None) -> str | None:
    if not value:
        return None
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def log_activity_event(
    session: Session,
    *,
    event_type: str,
    user: User | None = None,
    session_id: str | None = None,
    car_id: int | None = None,
    source: str | None = None,
    path: str | None = None,
    search_query: str | None = None,
    filters: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> ActivityEvent:
    event = ActivityEvent(
        event_type=event_type.strip()[:64],
        user_id=user.id if user else None,
        session_id=(session_id or "").strip()[:80] or None,
        car_id=car_id,
        source=(source or "").strip()[:80] or None,
        path=(path or "").strip()[:512] or None,
        search_query=(search_query or "").strip()[:256] or None,
        filters_json=_json_or_none(filters),
        metadata_json=_json_or_none(metadata),
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event
