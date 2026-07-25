from bson import ObjectId
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.database import get_db
from app.deps import require_admin
from app.models.audit import AuditLogEntry

router = APIRouter(prefix="/audit-logs", tags=["audit"], dependencies=[Depends(require_admin)])


class PaginatedAuditLogs(BaseModel):
    items: list[AuditLogEntry]
    total: int
    page: int
    page_size: int


@router.get("", response_model=PaginatedAuditLogs)
async def list_audit_logs(
    record_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
):
    db = get_db()
    query: dict = {}
    if record_id and ObjectId.is_valid(record_id):
        query["record_id"] = ObjectId(record_id)

    total = await db.audit_logs.count_documents(query)
    cursor = (
        db.audit_logs.find(query)
        .sort("created_at", -1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    docs = await cursor.to_list(length=page_size)
    items = [AuditLogEntry.model_validate(d) for d in docs]
    return PaginatedAuditLogs(items=items, total=total, page=page, page_size=page_size)
