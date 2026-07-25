from datetime import date, datetime, timezone
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.common import PyObjectId

EXPIRING_SOON_WINDOW_DAYS = 7


class BGStatus(str, Enum):
    ACTIVE = "Active"
    EXPIRING_SOON = "Expiring Soon"
    EXPIRED = "Expired"


def derive_status(expiry_date: date | datetime, today: date | None = None) -> BGStatus:
    today = today or datetime.now(timezone.utc).date()
    if isinstance(expiry_date, datetime):
        expiry_date = expiry_date.date()
    days_left = (expiry_date - today).days
    if days_left < 0:
        return BGStatus.EXPIRED
    if days_left <= EXPIRING_SOON_WINDOW_DAYS:
        return BGStatus.EXPIRING_SOON
    return BGStatus.ACTIVE


class BGRecordBase(BaseModel):
    bg_number: str = Field(min_length=1, max_length=100)
    name_of_work: str = Field(min_length=1, max_length=500)
    contractor_name: str = Field(min_length=1, max_length=200)
    issue_date: date
    expiry_date: date
    remarks: str = Field(default="", max_length=2000)
    assigned_to: str = Field(min_length=1, max_length=200)
    mobile_no: str = Field(min_length=10, max_length=15)
    email: EmailStr

    @field_validator("mobile_no")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        digits = v.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or not (10 <= len(digits) <= 15):
            raise ValueError("Invalid mobile number")
        return v

    @field_validator("expiry_date")
    @classmethod
    def expiry_after_issue(cls, v: date, info):
        issue_date = info.data.get("issue_date")
        if issue_date and v <= issue_date:
            raise ValueError("Expiry date must be after issue date")
        return v


class BGRecordCreate(BGRecordBase):
    pass


class BGRecordUpdate(BaseModel):
    bg_number: str | None = Field(default=None, min_length=1, max_length=100)
    name_of_work: str | None = Field(default=None, min_length=1, max_length=500)
    contractor_name: str | None = Field(default=None, min_length=1, max_length=200)
    issue_date: date | None = None
    expiry_date: date | None = None
    remarks: str | None = Field(default=None, max_length=2000)
    assigned_to: str | None = Field(default=None, min_length=1, max_length=200)
    mobile_no: str | None = Field(default=None, min_length=10, max_length=15)
    email: EmailStr | None = None


class BGRecordInDB(BGRecordBase):
    id: PyObjectId = Field(alias="_id")
    sr_no: int
    document_url: str | None = None
    document_public_id: str | None = None
    document_original_name: str | None = None
    is_deleted: bool = False
    deleted_at: datetime | None = None
    deleted_by: PyObjectId | None = None
    created_by: PyObjectId
    updated_by: PyObjectId | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}


class BGRecordOut(BaseModel):
    id: PyObjectId = Field(validation_alias="_id", serialization_alias="id")
    sr_no: int
    bg_number: str
    name_of_work: str
    contractor_name: str
    issue_date: date
    expiry_date: date
    remarks: str
    assigned_to: str
    mobile_no: str
    email: EmailStr
    document_url: str | None
    document_original_name: str | None
    status: BGStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}
