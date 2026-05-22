from datetime import datetime
from typing import Optional

from sqlalchemy import Column, LargeBinary, Text
from sqlmodel import Field, SQLModel


class MLTrainingRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(index=True, foreign_key="user.id")
    car_id: Optional[int] = Field(default=None, index=True, foreign_key="carlisting.id")

    vin_image_content_type: Optional[str] = Field(default=None)
    vin_image_bytes: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary, nullable=True))
    detected_vin: Optional[str] = Field(default=None, index=True)
    corrected_vin: Optional[str] = Field(default=None, index=True)
    model_confidence: Optional[float] = Field(default=None, index=True)

    decoded_make: Optional[str] = Field(default=None, index=True)
    decoded_model: Optional[str] = Field(default=None, index=True)
    decoded_year: Optional[int] = Field(default=None, index=True)

    price_prediction: Optional[int] = Field(default=None, index=True)
    price_model_name: Optional[str] = Field(default=None, index=True)
    price_model_version: Optional[str] = Field(default=None, index=True)
    price_prediction_created_at: Optional[datetime] = Field(default=None, index=True)
    final_listed_price: Optional[int] = Field(default=None, index=True)
    edited_listed_price: Optional[int] = Field(default=None, index=True)

    car_sold: bool = Field(default=False, index=True)
    final_sold_price: Optional[int] = Field(default=None, index=True)
    days_on_market: Optional[int] = Field(default=None, index=True)

    prediction_payload_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    price_prediction_raw_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    vin_decode_payload_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
