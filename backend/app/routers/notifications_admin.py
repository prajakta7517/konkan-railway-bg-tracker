from bson import ObjectId
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.database import get_db
from app.deps import require_admin
from app.models.notification import NotificationLogEntry
from app.services.notification_service import run_expiry_check

router = APIRouter(prefix="/notifications", tags=["notifications"], dependencies=[Depends(require_admin)])


class PaginatedNotifications(BaseModel):
    items: list[NotificationLogEntry]
    total: int
    page: int
    page_size: int


@router.get("", response_model=PaginatedNotifications)
async def list_notifications(
    bg_record_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
):
    db = get_db()
    query: dict = {}
    if bg_record_id and ObjectId.is_valid(bg_record_id):
        query["bg_record_id"] = ObjectId(bg_record_id)

    total = await db.notifications.count_documents(query)
    cursor = (
        db.notifications.find(query)
        .sort("sent_at", -1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    docs = await cursor.to_list(length=page_size)
    items = [NotificationLogEntry.model_validate(d) for d in docs]
    return PaginatedNotifications(items=items, total=total, page=page, page_size=page_size)


@router.post("/run-now")
async def trigger_expiry_check():
    """Manually trigger the expiry-check job (Admin only). Useful for testing;
    the production schedule is driven by the Render Cron Job, not this endpoint."""
    summary = await run_expiry_check()
    return summary
