from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.security import hash_password

pytestmark = pytest.mark.asyncio


async def _client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def _seed_admin(mock_db):
    await mock_db.users.insert_one(
        {
            "email": "admin@example.com",
            "full_name": "Test Admin",
            "hashed_password": hash_password("adminpass123"),
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }
    )


async def _seed_viewer(mock_db):
    await mock_db.users.insert_one(
        {
            "email": "viewer@example.com",
            "full_name": "Test Viewer",
            "hashed_password": hash_password("viewerpass123"),
            "role": "viewer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }
    )


async def test_full_flow(mock_db):
    await _seed_admin(mock_db)
    await _seed_viewer(mock_db)

    async with await _client() as client:
        # --- auth ---
        resp = await client.post(
            "/auth/login", json={"email": "admin@example.com", "password": "wrong"}
        )
        assert resp.status_code == 401

        resp = await client.post(
            "/auth/login", json={"email": "admin@example.com", "password": "adminpass123"}
        )
        assert resp.status_code == 200
        assert resp.cookies.get("access_token")

        resp = await client.get("/auth/me")
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

        # --- user management (admin only) ---
        resp = await client.get("/users")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

        # --- create BG record ---
        today = datetime.now(timezone.utc).date()
        issue_date = today - timedelta(days=30)
        expiry_date = today + timedelta(days=5)  # should land in "Expiring Soon"

        form = {
            "bg_number": "BG-2026-001",
            "name_of_work": "Track doubling — Ratnagiri section",
            "contractor_name": "ABC Infra Pvt Ltd",
            "issue_date": issue_date.isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "remarks": "Initial submission",
            "assigned_to": "Engineer A",
            "mobile_no": "9876543210",
            "email": "engineera@example.com",
        }
        resp = await client.post("/bg-records", data=form)
        assert resp.status_code == 201, resp.text
        record = resp.json()
        assert record["sr_no"] == 1
        assert record["status"] == "Expiring Soon"
        record_id = record["id"]

        # duplicate bg_number should be rejected
        resp = await client.post("/bg-records", data=form)
        assert resp.status_code == 409

        # --- list / search / filter ---
        resp = await client.get("/bg-records", params={"search": "Ratnagiri"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

        resp = await client.get("/bg-records", params={"status": "Expiring Soon"})
        assert resp.json()["total"] == 1

        resp = await client.get("/bg-records", params={"status": "Expired"})
        assert resp.json()["total"] == 0

        # --- update (admin only) ---
        resp = await client.patch(
            f"/bg-records/{record_id}", data={"remarks": "Renewed, extended validity"}
        )
        assert resp.status_code == 200
        assert resp.json()["remarks"] == "Renewed, extended validity"

        # --- soft delete ---
        resp = await client.delete(f"/bg-records/{record_id}")
        assert resp.status_code == 204

        resp = await client.get(f"/bg-records/{record_id}")
        assert resp.status_code == 404  # excluded once soft-deleted

        # --- audit log recorded create/update/delete ---
        resp = await client.get("/audit-logs")
        assert resp.status_code == 200
        actions = [entry["action"] for entry in resp.json()["items"]]
        assert set(actions) == {"create", "update", "delete"}

        await client.post("/auth/logout")

        # --- viewer cannot delete or manage users ---
        resp = await client.post(
            "/auth/login", json={"email": "viewer@example.com", "password": "viewerpass123"}
        )
        assert resp.status_code == 200

        resp = await client.get("/users")
        assert resp.status_code == 403

        form["bg_number"] = "BG-2026-002"
        resp = await client.post("/bg-records", data=form)
        assert resp.status_code == 201  # viewer can add

        new_id = resp.json()["id"]
        resp = await client.delete(f"/bg-records/{new_id}")
        assert resp.status_code == 403  # viewer cannot delete


async def test_forgot_and_reset_password(mock_db):
    await _seed_admin(mock_db)

    async with await _client() as client:
        resp = await client.post("/auth/forgot-password", json={"email": "admin@example.com"})
        assert resp.status_code == 200

        reset_doc = await mock_db.password_resets.find_one({})
        assert reset_doc is not None

        # We only have the hash stored (by design); simulate a client that has the
        # raw token by re-deriving through the same hashing path is not possible,
        # so instead verify the reset flow rejects an invalid token cleanly.
        resp = await client.post(
            "/auth/reset-password", json={"token": "not-a-real-token", "new_password": "newpass123"}
        )
        assert resp.status_code == 400


async def test_expiry_notification_service(mock_db):
    from app.services.notification_service import run_expiry_check

    today = datetime.now(timezone.utc).date()
    await mock_db.bg_records.insert_one(
        {
            "bg_number": "BG-NOTIFY-1",
            "name_of_work": "Test work",
            "contractor_name": "Test Contractor",
            "issue_date": datetime.combine(today - timedelta(days=100), datetime.min.time()),
            "expiry_date": datetime.combine(today + timedelta(days=3), datetime.min.time()),
            "remarks": "",
            "assigned_to": "Engineer B",
            "mobile_no": "9876500000",
            "email": "engineerb@example.com",
            "sr_no": 1,
            "document_url": None,
            "document_public_id": None,
            "document_original_name": None,
            "is_deleted": False,
            "deleted_at": None,
            "deleted_by": None,
            "created_by": None,
            "updated_by": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    summary = await run_expiry_check()
    assert summary["checked"] == 1
    # No MAIL_USERNAME/MAIL_PASSWORD configured in the test env, so the send should be
    # logged as failed rather than raising -- confirms the job is resilient.
    assert summary["sent"] + summary["failed"] == 1

    notif = await mock_db.notifications.find_one({"bg_number": "BG-NOTIFY-1"})
    assert notif is not None
    assert notif["days_before_expiry"] == 3

    # Re-running the same day should not send a duplicate for the same day count.
    summary2 = await run_expiry_check()
    assert summary2["skipped_already_sent"] + summary2["sent"] + summary2["failed"] >= 1
    count = await mock_db.notifications.count_documents({"bg_number": "BG-NOTIFY-1"})
    assert count == 1
