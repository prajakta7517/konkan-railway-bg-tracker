import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING

from app.config import get_settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        settings = get_settings()
        _db = get_client()[settings.db_name]
    return _db


async def ensure_indexes() -> None:
    db = get_db()

    await db.users.create_index([("email", ASCENDING)], unique=True)

    await db.bg_records.create_index([("bg_number", ASCENDING)], unique=True)
    await db.bg_records.create_index([("expiry_date", ASCENDING)])
    await db.bg_records.create_index([("is_deleted", ASCENDING)])
    await db.bg_records.create_index(
        [("contractor_name", ASCENDING), ("name_of_work", ASCENDING)]
    )

    await db.notifications.create_index(
        [("bg_record_id", ASCENDING), ("days_before_expiry", ASCENDING)]
    )

    await db.audit_logs.create_index([("record_id", ASCENDING)])
    await db.audit_logs.create_index([("created_at", ASCENDING)])

    await db.password_resets.create_index([("token_hash", ASCENDING)], unique=True)
    await db.password_resets.create_index(
        [("expires_at", ASCENDING)], expireAfterSeconds=0
    )

    logger.info("MongoDB indexes ensured")


async def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
