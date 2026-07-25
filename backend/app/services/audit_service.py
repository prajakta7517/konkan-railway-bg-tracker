from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from app.database import get_db
from app.models.audit import AuditAction


async def log_audit(
    record_id: str,
    action: AuditAction,
    changed_by_id: str,
    changed_by_email: str,
    changes: dict[str, Any] | None = None,
) -> None:
    db = get_db()
    await db.audit_logs.insert_one(
        {
            "record_id": ObjectId(record_id),
            "action": action.value,
            "changed_by": ObjectId(changed_by_id),
            "changed_by_email": changed_by_email,
            "changes": changes or {},
            "created_at": datetime.now(timezone.utc),
        }
    )
