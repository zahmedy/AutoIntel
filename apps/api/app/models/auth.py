from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class EmailVerificationCode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    email: str = Field(index=True, max_length=255)
    purpose: str = Field(default="email_login", index=True, max_length=64)
    code_hash: str = Field(max_length=128)
    attempts: int = Field(default=0, index=True)

    expires_at: datetime = Field(index=True)
    consumed_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
