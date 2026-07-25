"""Daily BG expiry-check job, intended to be run by a Render Cron Job.

Render Cron Job command (from the backend/ root, after `pip install -r requirements.txt`):
    python -m scripts.expiry_check

Runs independently of the web service, so notifications still fire even if the
web service has spun down from inactivity on Render's free tier.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import close_client, ensure_indexes  # noqa: E402
from app.services.notification_service import run_expiry_check  # noqa: E402


async def main() -> None:
    await ensure_indexes()
    summary = await run_expiry_check()
    print(summary)
    await close_client()


if __name__ == "__main__":
    asyncio.run(main())
