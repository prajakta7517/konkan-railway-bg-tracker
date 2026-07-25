"""One-off script to bootstrap the first Admin user.

Usage (from backend/ with venv active):
    python -m scripts.create_admin

Reads FIRST_ADMIN_EMAIL / FIRST_ADMIN_PASSWORD from the environment (.env).
Safe to re-run: it will not create a duplicate if the user already exists.
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.database import get_db  # noqa: E402
from app.security import hash_password  # noqa: E402


async def main() -> None:
    settings = get_settings()
    if not settings.first_admin_email or not settings.first_admin_password:
        print("Set FIRST_ADMIN_EMAIL and FIRST_ADMIN_PASSWORD in your .env first.")
        return

    db = get_db()
    existing = await db.users.find_one({"email": settings.first_admin_email.lower()})
    if existing:
        print(f"User {settings.first_admin_email} already exists (role={existing['role']}).")
        return

    await db.users.insert_one(
        {
            "email": settings.first_admin_email.lower(),
            "full_name": "System Administrator",
            "hashed_password": hash_password(settings.first_admin_password),
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }
    )
    print(f"Admin user created: {settings.first_admin_email}")


if __name__ == "__main__":
    asyncio.run(main())
