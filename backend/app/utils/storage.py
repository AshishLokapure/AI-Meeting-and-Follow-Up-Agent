from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from mutagen import File as MutagenFile

from app.core.settings import get_settings

ALLOWED_AUDIO_CONTENT_TYPES = {
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mp4": ".mp4",
    "video/mp4": ".mp4",
    "audio/x-m4a": ".m4a",
    "audio/m4a": ".m4a",
}

ALLOWED_DOCUMENT_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
}


class StorageCategory(str, Enum):
    audio = "audio"
    transcripts = "transcripts"
    documents = "documents"


@dataclass(frozen=True)
class StorageResult:
    url: str
    storage_key: str
    filename: str
    size_bytes: int
    content_type: str | None


def _storage_root() -> Path:
    settings = get_settings()
    root = Path(settings.uploads_root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def _category_directory(category: StorageCategory) -> Path:
    directory = _storage_root() / category.value
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def validate_upload_file(upload_file: UploadFile, *, category: StorageCategory) -> str:
    if category == StorageCategory.audio:
        allowed_types = ALLOWED_AUDIO_CONTENT_TYPES
    else:
        allowed_types = ALLOWED_DOCUMENT_CONTENT_TYPES

    if upload_file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file format")
    return allowed_types[upload_file.content_type]


def _build_local_url(category: StorageCategory, filename: str) -> str:
    return f"/uploads/{category.value}/{filename}"


def _build_s3_url(bucket_name: str, region: str, key: str) -> str:
    return f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"


def _persist_to_local(category: StorageCategory, temp_path: Path, final_filename: str) -> str:
    final_path = _category_directory(category) / final_filename
    temp_path.replace(final_path)
    return _build_local_url(category, final_filename)


def _persist_to_s3(category: StorageCategory, temp_path: Path, final_filename: str, content_type: str | None) -> str:
    settings = get_settings()
    if not settings.aws_bucket_name:
        temp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AWS bucket is not configured")

    try:
        import boto3
    except ImportError as exc:
        temp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="S3 storage backend is unavailable") from exc

    key_prefix = settings.aws_s3_prefix.strip("/")
    storage_key = f"{key_prefix}/{category.value}/{final_filename}" if key_prefix else f"{category.value}/{final_filename}"
    s3_client = boto3.client("s3", region_name=settings.aws_region)
    with temp_path.open("rb") as source_file:
        s3_client.upload_fileobj(
            source_file,
            settings.aws_bucket_name,
            storage_key,
            ExtraArgs={"ContentType": content_type or "application/octet-stream"},
        )

    temp_path.unlink(missing_ok=True)
    return _build_s3_url(settings.aws_bucket_name, settings.aws_region, storage_key)


def store_upload_file(
    upload_file: UploadFile,
    *,
    category: StorageCategory,
    validate_type: bool = True,
) -> StorageResult:
    settings = get_settings()
    suffix = validate_upload_file(upload_file, category=category) if validate_type else Path(upload_file.filename or "").suffix or ".bin"
    upload_id = str(uuid4())
    temp_path = _category_directory(category) / f"{upload_id}.tmp"

    bytes_written = 0
    with temp_path.open("wb") as target_file:
        while chunk := upload_file.file.read(1024 * 1024):
            bytes_written += len(chunk)
            if bytes_written > settings.max_upload_size_mb * 1024 * 1024:
                temp_path.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds maximum size")
            target_file.write(chunk)

    final_filename = f"{upload_id}{suffix}"
    if settings.storage_backend.lower() == "s3":
        url = _persist_to_s3(category, temp_path, final_filename, upload_file.content_type)
        storage_key = f"{settings.aws_s3_prefix.strip('/')}/{category.value}/{final_filename}" if settings.aws_s3_prefix.strip('/') else f"{category.value}/{final_filename}"
    else:
        url = _persist_to_local(category, temp_path, final_filename)
        storage_key = f"{category.value}/{final_filename}"

    return StorageResult(
        url=url,
        storage_key=storage_key,
        filename=final_filename,
        size_bytes=bytes_written,
        content_type=upload_file.content_type,
    )


def store_meeting_audio(upload_file: UploadFile) -> StorageResult:
    return store_upload_file(upload_file, category=StorageCategory.audio)


def store_transcript_text(meeting_id: str, transcript_text: str) -> StorageResult:
    settings = get_settings()
    temp_path = _category_directory(StorageCategory.transcripts) / f"{meeting_id}.tmp"
    encoded = transcript_text.encode("utf-8")
    if len(encoded) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Transcript exceeds maximum size")

    temp_path.write_bytes(encoded)
    final_filename = f"{meeting_id}.txt"
    if settings.storage_backend.lower() == "s3":
        url = _persist_to_s3(StorageCategory.transcripts, temp_path, final_filename, "text/plain")
        storage_key = f"{settings.aws_s3_prefix.strip('/')}/{StorageCategory.transcripts.value}/{final_filename}" if settings.aws_s3_prefix.strip('/') else f"{StorageCategory.transcripts.value}/{final_filename}"
    else:
        url = _persist_to_local(StorageCategory.transcripts, temp_path, final_filename)
        storage_key = f"{StorageCategory.transcripts.value}/{final_filename}"

    return StorageResult(
        url=url,
        storage_key=storage_key,
        filename=final_filename,
        size_bytes=len(encoded),
        content_type="text/plain",
    )


def store_document_upload(upload_file: UploadFile) -> StorageResult:
    return store_upload_file(upload_file, category=StorageCategory.documents)
