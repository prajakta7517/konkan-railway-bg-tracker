from bson import ObjectId
from fastapi import Cookie, Header, HTTPException, status

from app.config import get_settings
from app.database import get_db
from app.models.user import UserOut, UserRole
from app.security import decode_token

ACCESS_COOKIE_NAME = "access_token"


async def get_current_user(
    access_token: str | None = Cookie(default=None, alias=ACCESS_COOKIE_NAME),
) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
    if not access_token:
        raise credentials_exception

    payload = decode_token(access_token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id or not ObjectId.is_valid(user_id):
        raise credentials_exception

    db = get_db()
    user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise credentials_exception
    if not user_doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
        )

    return UserOut.model_validate(user_doc)


def require_role(*roles: UserRole):
    async def checker(
        access_token: str | None = Cookie(default=None, alias=ACCESS_COOKIE_NAME),
    ) -> UserOut:
        user = await get_current_user(access_token)
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return user

    return checker


require_admin = require_role(UserRole.ADMIN)
require_any_role = require_role(UserRole.ADMIN, UserRole.VIEWER)


async def verify_cron_secret(x_cron_secret: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not settings.cron_secret or x_cron_secret != settings.cron_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid cron secret"
        )
