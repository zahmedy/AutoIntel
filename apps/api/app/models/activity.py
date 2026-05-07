from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ActivityEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    event_type: str = Field(index=True, max_length=64)
    user_id: Optional[int] = Field(default=None, index=True, foreign_key="user.id")
    session_id: Optional[str] = Field(default=None, index=True, max_length=80)
    car_id: Optional[int] = Field(default=None, index=True, foreign_key="carlisting.id")

    source: Optional[str] = Field(default=None, index=True, max_length=80)
    path: Optional[str] = Field(default=None, max_length=512)
    search_query: Optional[str] = Field(default=None, index=True, max_length=256)
    filters_json: Optional[str] = None
    metadata_json: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
