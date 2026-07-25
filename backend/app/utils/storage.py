from pathlib import Path
from typing import BinaryIO

from fastapi import UploadFile, HTTPException, status

from app.core.settings import get_settings

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}


def _avatar_directory() -> Path:
    settings = get_settings()
    directory = Path(settings.uploads_root) / "avatars"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_avatar_file(user_id: str, upload_file: UploadFile) -> str:
    if upload_file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported avatar image type")

    suffix = ALLOWED_IMAGE_CONTENT_TYPES[upload_file.content_type]
    filename = f"{user_id}{suffix}"
    file_path = _avatar_directory() / filename

    with file_path.open("wb") as target_file:
        while chunk := upload_file.file.read(1024 * 1024):
            target_file.write(chunk)

    return f"/uploads/avatars/{filename}"


def delete_avatar_file(avatar_url: str | None) -> None:
    if not avatar_url:
        return

    relative_path = avatar_url.lstrip("/")
    file_path = Path(relative_path)
    if not file_path.is_absolute():
        file_path = Path(".") / file_path
    if file_path.exists():
        file_path.unlink()
