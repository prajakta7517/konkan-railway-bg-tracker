from datetime import datetime, timedelta, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.config import get_settings
from app.database import get_db
from app.deps import ACCESS_COOKIE_NAME, get_current_user
from app.models.user import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserLogin,
    UserOut,
)
from app.rate_limit import limiter
from app.security import (
    create_access_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password,
)
from app.services.email_service import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


@router.post("/login", response_model=UserOut)
@limiter.limit("5/minute")
async def login(request: Request, response: Response, credentials: UserLogin):
    db = get_db()
    user_doc = await db.users.find_one({"email": credentials.email.lower()})

    generic_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
    )

    if not user_doc or not verify_password(credentials.password, user_doc["hashed_password"]):
        raise generic_error

    if not user_doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
        )

    token = create_access_token(str(user_doc["_id"]), user_doc["role"])
    _set_auth_cookie(response, token)
    return UserOut.model_validate(user_doc)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserOut)
async def me(current_user: UserOut = Depends(get_current_user)):
    return current_user


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest, current_user: UserOut = Depends(get_current_user)
):
    db = get_db()
    user_doc = await db.users.find_one({"_id": ObjectId(current_user.id)})
    if not user_doc or not verify_password(body.current_password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"hashed_password": hash_password(body.new_password)}},
    )
    return {"detail": "Password updated"}


@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, body: ForgotPasswordRequest):
    db = get_db()
    settings = get_settings()
    user_doc = await db.users.find_one({"email": body.email.lower()})

    # Always return a generic response to avoid leaking whether an email is registered.
    generic_response = {
        "detail": "If an account with that email exists, a reset link has been sent."
    }

    if not user_doc or not user_doc.get("is_active", True):
        return generic_response

    raw_token, token_hash = generate_reset_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.reset_token_expire_minutes
    )
    await db.password_resets.delete_many({"user_id": user_doc["_id"]})
    await db.password_resets.insert_one(
        {
            "user_id": user_doc["_id"],
            "token_hash": token_hash,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc),
        }
    )

    reset_url = f"{settings.frontend_url}/reset-password?token={raw_token}"
    send_password_reset_email(user_doc["email"], reset_url)

    return generic_response


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request, body: ResetPasswordRequest):
    db = get_db()
    token_hash = hash_reset_token(body.token)
    reset_doc = await db.password_resets.find_one({"token_hash": token_hash})

    invalid_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="This reset link is invalid or has expired",
    )

    if not reset_doc:
        raise invalid_exception

    expires_at = reset_doc["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        await db.password_resets.delete_one({"_id": reset_doc["_id"]})
        raise invalid_exception

    await db.users.update_one(
        {"_id": reset_doc["user_id"]},
        {"$set": {"hashed_password": hash_password(body.new_password)}},
    )
    await db.password_resets.delete_many({"user_id": reset_doc["user_id"]})

    return {"detail": "Password has been reset. You can now log in."}
