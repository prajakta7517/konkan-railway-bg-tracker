from datetime import date, datetime, timedelta, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, ValidationError
from pymongo import ReturnDocument

from app.database import get_db
from app.deps import get_current_user, require_admin, require_any_role
from app.models.audit import AuditAction
from app.models.bg_record import (
    BGRecordCreate,
    BGRecordOut,
    BGStatus,
    EXPIRING_SOON_WINDOW_DAYS,
    derive_status,
)
from app.models.user import UserOut
from app.services.audit_service import log_audit
from app.services.cloudinary_service import delete_bg_document, upload_bg_document
from app.services.counter_service import next_sequence

router = APIRouter(prefix="/bg-records", tags=["bg-records"])


class PaginatedBGRecords(BaseModel):
    items: list[BGRecordOut]
    total: int
    page: int
    page_size: int


def _doc_to_out(doc: dict) -> dict:
    doc = dict(doc)
    doc["status"] = derive_status(doc["expiry_date"])
    return doc


def _status_date_filter(bg_status: BGStatus, today: date) -> dict:
    # BSON has no date-only type, so all boundaries must be datetimes.
    today_dt = datetime.combine(today, datetime.min.time())
    window_end_dt = today_dt + timedelta(days=EXPIRING_SOON_WINDOW_DAYS)
    if bg_status == BGStatus.EXPIRED:
        return {"expiry_date": {"$lt": today_dt}}
    if bg_status == BGStatus.EXPIRING_SOON:
        return {"expiry_date": {"$gte": today_dt, "$lte": window_end_dt}}
    return {"expiry_date": {"$gt": window_end_dt}}


@router.get("", response_model=PaginatedBGRecords)
async def list_bg_records(
    search: str | None = Query(default=None, max_length=200),
    status_filter: BGStatus | None = Query(default=None, alias="status"),
    sort_by: str = Query(default="expiry_date"),
    sort_dir: int = Query(default=1, ge=-1, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
    _user: UserOut = Depends(get_current_user),
):
    db = get_db()
    today = datetime.now(timezone.utc).date()

    query: dict = {"is_deleted": False}
    if search:
        regex = {"$regex": search, "$options": "i"}
        query["$or"] = [
            {"bg_number": regex},
            {"name_of_work": regex},
            {"contractor_name": regex},
        ]
    if status_filter:
        query.update(_status_date_filter(status_filter, today))

    allowed_sort_fields = {
        "expiry_date",
        "issue_date",
        "bg_number",
        "contractor_name",
        "sr_no",
        "created_at",
    }
    if sort_by not in allowed_sort_fields:
        sort_by = "expiry_date"

    total = await db.bg_records.count_documents(query)
    cursor = (
        db.bg_records.find(query)
        .sort(sort_by, sort_dir)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    docs = await cursor.to_list(length=page_size)

    items = [BGRecordOut.model_validate(_doc_to_out(d)) for d in docs]
    return PaginatedBGRecords(items=items, total=total, page=page, page_size=page_size)


@router.get("/{record_id}", response_model=BGRecordOut)
async def get_bg_record(record_id: str, _user: UserOut = Depends(get_current_user)):
    if not ObjectId.is_valid(record_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid record id")
    db = get_db()
    doc = await db.bg_records.find_one({"_id": ObjectId(record_id), "is_deleted": False})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return BGRecordOut.model_validate(_doc_to_out(doc))


@router.post("", response_model=BGRecordOut, status_code=status.HTTP_201_CREATED)
async def create_bg_record(
    bg_number: str = Form(...),
    name_of_work: str = Form(...),
    contractor_name: str = Form(...),
    issue_date: date = Form(...),
    expiry_date: date = Form(...),
    remarks: str = Form(default=""),
    assigned_to: str = Form(...),
    mobile_no: str = Form(...),
    email: EmailStr = Form(...),
    file: UploadFile | None = File(default=None),
    current_user: UserOut = Depends(require_any_role),
):
    try:
        payload = BGRecordCreate(
            bg_number=bg_number,
            name_of_work=name_of_work,
            contractor_name=contractor_name,
            issue_date=issue_date,
            expiry_date=expiry_date,
            remarks=remarks,
            assigned_to=assigned_to,
            mobile_no=mobile_no,
            email=email,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())

    db = get_db()
    existing = await db.bg_records.find_one({"bg_number": payload.bg_number})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A record with this Bank Guarantee Number already exists",
        )

    doc = payload.model_dump()
    doc["issue_date"] = datetime.combine(payload.issue_date, datetime.min.time())
    doc["expiry_date"] = datetime.combine(payload.expiry_date, datetime.min.time())
    doc["sr_no"] = await next_sequence("bg_record")
    doc["document_url"] = None
    doc["document_public_id"] = None
    doc["document_original_name"] = None
    doc["is_deleted"] = False
    doc["deleted_at"] = None
    doc["deleted_by"] = None
    doc["created_by"] = ObjectId(current_user.id)
    doc["updated_by"] = None
    doc["created_at"] = datetime.now(timezone.utc)
    doc["updated_at"] = datetime.now(timezone.utc)

    if file is not None and file.filename:
        upload_result = await upload_bg_document(file)
        doc["document_url"] = upload_result["document_url"]
        doc["document_public_id"] = upload_result["document_public_id"]
        doc["document_original_name"] = upload_result["document_original_name"]

    result = await db.bg_records.insert_one(doc)
    doc["_id"] = result.inserted_id

    await log_audit(
        record_id=str(result.inserted_id),
        action=AuditAction.CREATE,
        changed_by_id=current_user.id,
        changed_by_email=current_user.email,
        changes=jsonable_encoder(payload.model_dump()),
    )

    return BGRecordOut.model_validate(_doc_to_out(doc))


@router.patch("/{record_id}", response_model=BGRecordOut)
async def update_bg_record(
    record_id: str,
    bg_number: str | None = Form(default=None),
    name_of_work: str | None = Form(default=None),
    contractor_name: str | None = Form(default=None),
    issue_date: date | None = Form(default=None),
    expiry_date: date | None = Form(default=None),
    remarks: str | None = Form(default=None),
    assigned_to: str | None = Form(default=None),
    mobile_no: str | None = Form(default=None),
    email: EmailStr | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    current_user: UserOut = Depends(require_admin),
):
    if not ObjectId.is_valid(record_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid record id")

    db = get_db()
    existing = await db.bg_records.find_one({"_id": ObjectId(record_id), "is_deleted": False})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    updates: dict = {}
    raw_fields = {
        "bg_number": bg_number,
        "name_of_work": name_of_work,
        "contractor_name": contractor_name,
        "remarks": remarks,
        "assigned_to": assigned_to,
        "mobile_no": mobile_no,
        "email": email,
    }
    for key, value in raw_fields.items():
        if value is not None:
            updates[key] = value

    if issue_date is not None:
        updates["issue_date"] = datetime.combine(issue_date, datetime.min.time())
    if expiry_date is not None:
        updates["expiry_date"] = datetime.combine(expiry_date, datetime.min.time())

    if updates.get("bg_number") and updates["bg_number"] != existing["bg_number"]:
        clash = await db.bg_records.find_one(
            {"bg_number": updates["bg_number"], "_id": {"$ne": ObjectId(record_id)}}
        )
        if clash:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A record with this Bank Guarantee Number already exists",
            )

    if file is not None and file.filename:
        upload_result = await upload_bg_document(file)
        updates["document_url"] = upload_result["document_url"]
        updates["document_public_id"] = upload_result["document_public_id"]
        updates["document_original_name"] = upload_result["document_original_name"]
        old_public_id = existing.get("document_public_id")
        if old_public_id:
            delete_bg_document(old_public_id)

    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    updates["updated_by"] = ObjectId(current_user.id)
    updates["updated_at"] = datetime.now(timezone.utc)

    updated_doc = await db.bg_records.find_one_and_update(
        {"_id": ObjectId(record_id)},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )

    await log_audit(
        record_id=record_id,
        action=AuditAction.UPDATE,
        changed_by_id=current_user.id,
        changed_by_email=current_user.email,
        changes=jsonable_encoder(updates, exclude={"updated_by"}),
    )

    return BGRecordOut.model_validate(_doc_to_out(updated_doc))


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bg_record(record_id: str, current_user: UserOut = Depends(require_admin)):
    if not ObjectId.is_valid(record_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid record id")

    db = get_db()
    result = await db.bg_records.find_one_and_update(
        {"_id": ObjectId(record_id), "is_deleted": False},
        {
            "$set": {
                "is_deleted": True,
                "deleted_at": datetime.now(timezone.utc),
                "deleted_by": ObjectId(current_user.id),
            }
        },
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    await log_audit(
        record_id=record_id,
        action=AuditAction.SOFT_DELETE,
        changed_by_id=current_user.id,
        changed_by_email=current_user.email,
    )
    return None
