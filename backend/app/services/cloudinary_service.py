import logging
import uuid

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from app.config import get_settings

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "docx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

_configured = False


def _ensure_configured() -> None:
    global _configured
    if _configured:
        return
    settings = get_settings()
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    _configured = True


def _validate_file(file: UploadFile, contents: bytes) -> str:
    extension = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File exceeds the 10MB size limit",
        )
    return extension


async def upload_bg_document(file: UploadFile) -> dict:
    _ensure_configured()
    contents = await file.read()
    extension = _validate_file(file, contents)

    public_id = f"bg_documents/{uuid.uuid4().hex}"
    try:
        result = cloudinary.uploader.upload(
            contents,
            public_id=public_id,
            resource_type="raw" if extension in {"pdf", "docx"} else "image",
            overwrite=False,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Cloudinary upload failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to upload document to storage",
        ) from exc

    return {
        "document_url": result.get("secure_url"),
        "document_public_id": result.get("public_id"),
        "document_original_name": file.filename,
        "resource_type": result.get("resource_type"),
    }


def delete_bg_document(public_id: str, resource_type: str = "raw") -> None:
    _ensure_configured()
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to delete Cloudinary document %s", public_id)
