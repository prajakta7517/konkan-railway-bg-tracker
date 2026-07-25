from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

from app.models.common import PyObjectId


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"  # reserved for future use


class NotificationStatus(str, Enum):
    SENT = "sent"
    FAILED = "failed"


class NotificationLogEntry(BaseModel):
    id: PyObjectId = Field(validation_alias="_id", serialization_alias="id")
    bg_record_id: PyObjectId
    bg_number: str
    channel: NotificationChannel
    recipient: str
    days_before_expiry: int
    status: NotificationStatus
    error_message: str | None = None
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}
