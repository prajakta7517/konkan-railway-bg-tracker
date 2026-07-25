from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, EmailStr, Field

from app.models.common import PyObjectId


class UserRole(str, Enum):
    ADMIN = "admin"
    VIEWER = "viewer"  # viewer / data-entry: can add & view records


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=200)
    role: UserRole = UserRole.VIEWER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: PyObjectId = Field(validation_alias="_id", serialization_alias="id")
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"populate_by_name": True}


class UserInDB(BaseModel):
    id: PyObjectId = Field(alias="_id")
    email: EmailStr
    full_name: str
    hashed_password: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UpdateUserRole(BaseModel):
    role: UserRole


class UpdateUserActive(BaseModel):
    is_active: bool
