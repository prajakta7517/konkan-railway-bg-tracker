from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.models.common import PyObjectId


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    SOFT_DELETE = "delete"
    RESTORE = "restore"


class AuditLogEntry(BaseModel):
    id: PyObjectId = Field(validation_alias="_id", serialization_alias="id")
    record_id: PyObjectId
    action: AuditAction
    changed_by: PyObjectId
    changed_by_email: str
    changes: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}
