from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.settings import get_settings

ALLOWED_AVATAR_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _avatar_root() -> Path:
    settings = get_settings()
    root = Path(settings.uploads_root) / "avatars"
    root.mkdir(parents=True, exist_ok=True)
    return root


def save_avatar_file(user_id: str, avatar: UploadFile) -> str:
    if avatar.content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported avatar format")

    suffix = ALLOWED_AVATAR_CONTENT_TYPES[avatar.content_type]
    avatar_id = uuid4().hex
    filename = f"{user_id}-{avatar_id}{suffix}"
    destination = _avatar_root() / filename

    bytes_written = 0
    with destination.open("wb") as target_file:
        while chunk := avatar.file.read(1024 * 1024):
            bytes_written += len(chunk)
            if bytes_written > 10 * 1024 * 1024:
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Avatar exceeds maximum size")
            target_file.write(chunk)

    return f"/uploads/avatars/{filename}"


def delete_avatar_file(avatar_url: str | None) -> None:
    if not avatar_url:
        return

    filename = Path(avatar_url).name
    if not filename:
        return

    file_path = _avatar_root() / filename
    file_path.unlink(missing_ok=True)
