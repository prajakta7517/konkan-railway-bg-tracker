from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import ReturnDocument

from app.database import get_db
from app.deps import require_admin
from app.models.user import (
    UpdateUserActive,
    UpdateUserRole,
    UserCreate,
    UserOut,
)
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[UserOut])
async def list_users():
    db = get_db()
    users = await db.users.find().sort("created_at", 1).to_list(length=1000)
    return [UserOut.model_validate(u) for u in users]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate):
    db = get_db()
    existing = await db.users.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists"
        )

    doc = {
        "email": body.email.lower(),
        "full_name": body.full_name,
        "hashed_password": hash_password(body.password),
        "role": body.role.value,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return UserOut.model_validate(doc)


@router.patch("/{user_id}/role", response_model=UserOut)
async def update_user_role(user_id: str, body: UpdateUserRole):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")
    db = get_db()
    result = await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": body.role.value}},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserOut.model_validate(result)


@router.patch("/{user_id}/active", response_model=UserOut)
async def update_user_active(user_id: str, body: UpdateUserActive):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")
    db = get_db()
    result = await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": body.is_active}},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserOut.model_validate(result)
