from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ActivityEventCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=64)
    session_id: str | None = Field(default=None, max_length=80)
    car_id: int | None = None
    source: str | None = Field(default=None, max_length=80)
    path: str | None = Field(default=None, max_length=512)
    search_query: str | None = Field(default=None, max_length=256)
    filters: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActivityEventOut(BaseModel):
    id: int
    event_type: str
    user_id: int | None
    session_id: str | None
    car_id: int | None
    source: str | None
    path: str | None
    search_query: str | None
    created_at: datetime
