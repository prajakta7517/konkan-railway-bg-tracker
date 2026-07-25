import logging
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.models.bg_record import EXPIRING_SOON_WINDOW_DAYS
from app.services.email_service import send_bg_expiry_email

logger = logging.getLogger(__name__)


async def run_expiry_check() -> dict:
    """Send countdown email alerts for BG records expiring in 1-7 days.

    Idempotent: re-running on the same day will not send duplicate emails,
    because each (record, days_before_expiry) pair is only ever notified once
    (checked against the notifications collection before sending).
    """
    db = get_db()
    today = datetime.now(timezone.utc).date()
    window_start = datetime.combine(today, datetime.min.time())
    window_end = window_start + timedelta(days=EXPIRING_SOON_WINDOW_DAYS)

    cursor = db.bg_records.find(
        {
            "is_deleted": False,
            "expiry_date": {"$gte": window_start, "$lte": window_end},
        }
    )

    checked = 0
    sent = 0
    skipped_already_sent = 0
    failed = 0

    async for record in cursor:
        checked += 1
        expiry_date = record["expiry_date"]
        if isinstance(expiry_date, datetime):
            expiry_date = expiry_date.date()
        days_left = (expiry_date - today).days

        if not (1 <= days_left <= EXPIRING_SOON_WINDOW_DAYS):
            continue

        notif_key = {
            "bg_record_id": record["_id"],
            "days_before_expiry": days_left,
            "channel": "email",
        }
        existing_notif = await db.notifications.find_one(notif_key)
        if existing_notif and existing_notif.get("status") == "sent":
            skipped_already_sent += 1
            continue

        ok, error = send_bg_expiry_email(
            to_email=record["email"],
            assigned_to=record["assigned_to"],
            bg_number=record["bg_number"],
            name_of_work=record["name_of_work"],
            contractor_name=record["contractor_name"],
            expiry_date=expiry_date.isoformat(),
            days_left=days_left,
        )

        await db.notifications.update_one(
            notif_key,
            {
                "$set": {
                    "bg_number": record["bg_number"],
                    "recipient": record["email"],
                    "status": "sent" if ok else "failed",
                    "error_message": error,
                    "sent_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )

        if ok:
            sent += 1
        else:
            failed += 1
            logger.error(
                "Failed to send expiry notification for %s: %s", record["bg_number"], error
            )

    summary = {
        "checked": checked,
        "sent": sent,
        "skipped_already_sent": skipped_already_sent,
        "failed": failed,
        "run_at": datetime.now(timezone.utc).isoformat(),
    }
    logger.info("Expiry check complete: %s", summary)
    return summary
