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
    "video/quicktime": ".mov",
    "video/webm": ".webm",
    "video/x-matroska": ".mkv",
    "video/x-msvideo": ".avi",
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
    video = "videos"
    transcripts = "transcripts"
    documents = "documents"


@dataclass(frozen=True)
class StorageResult:
    url: str
    storage_key: str
    filename: str
    size_bytes: int
    content_type: str | None
    duration_seconds: float | None = None
    audio_url: str | None = None
    audio_storage_key: str | None = None
    audio_filename: str | None = None


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
    suffix = Path(upload_file.filename or "").suffix.lower()
    if category in {StorageCategory.audio, StorageCategory.video}:
        allowed_suffixes = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".mp3", ".wav", ".m4a"}
        allowed_types = {
            "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/mp4",
            "audio/x-m4a", "audio/m4a", "video/mp4", "video/quicktime",
            "video/webm", "video/x-matroska", "video/x-msvideo",
        }
        if upload_file.content_type in allowed_types and suffix in allowed_suffixes:
            return suffix
        if suffix in allowed_suffixes:
            return suffix
    elif upload_file.content_type in ALLOWED_DOCUMENT_CONTENT_TYPES:
        return ALLOWED_DOCUMENT_CONTENT_TYPES[upload_file.content_type]
    raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file format")

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


def _read_audio_duration(temp_path: Path) -> float:
    audio = MutagenFile(str(temp_path))
    if audio is None or not getattr(audio, "info", None) or not getattr(audio.info, "length", None):
        temp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not read audio duration")
    return float(audio.info.length)


def store_audio_upload(upload_file: UploadFile) -> StorageResult:
    settings = get_settings()
    suffix = validate_upload_file(upload_file, category=StorageCategory.audio)
    upload_id = str(uuid4())
    temp_path = _category_directory(StorageCategory.audio) / f"{upload_id}.tmp"

    bytes_written = 0
    with temp_path.open("wb") as target_file:
        while chunk := upload_file.file.read(1024 * 1024):
            bytes_written += len(chunk)
            if bytes_written > settings.max_upload_size_mb * 1024 * 1024:
                temp_path.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds maximum size")
            target_file.write(chunk)

    duration_seconds = _read_audio_duration(temp_path)
    if duration_seconds > settings.max_meeting_duration_minutes * 60:
        temp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Meeting duration exceeds maximum allowed length")

    final_filename = f"{upload_id}{suffix}"
    if settings.storage_backend.lower() == "s3":
        url = _persist_to_s3(StorageCategory.audio, temp_path, final_filename, upload_file.content_type)
        key_prefix = settings.aws_s3_prefix.strip("/")
        storage_key = f"{key_prefix}/{StorageCategory.audio.value}/{final_filename}" if key_prefix else f"{StorageCategory.audio.value}/{final_filename}"
    else:
        url = _persist_to_local(StorageCategory.audio, temp_path, final_filename)
        storage_key = f"{StorageCategory.audio.value}/{final_filename}"

    return StorageResult(
        url=url,
        storage_key=storage_key,
        filename=final_filename,
        size_bytes=bytes_written,
        content_type=upload_file.content_type,
        duration_seconds=duration_seconds,
    )


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
        key_prefix = settings.aws_s3_prefix.strip("/")
        storage_key = f"{key_prefix}/{category.value}/{final_filename}" if key_prefix else f"{category.value}/{final_filename}"
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


def store_video_upload(upload_file: UploadFile) -> StorageResult:
    """Store the original video; conversion is performed by the worker."""
    settings = get_settings()
    suffix = validate_upload_file(upload_file, category=StorageCategory.video)
    source_name = Path(upload_file.filename or "meeting").name
    stem = Path(source_name).stem or "meeting"
    safe_stem = "".join(character if character.isalnum() or character in "-_" else "_" for character in stem)
    final_filename = f"{safe_stem}{suffix}"
    video_directory = _category_directory(StorageCategory.video)
    final_path = video_directory / final_filename
    if final_path.exists():
        final_filename = f"{safe_stem}-{uuid4().hex[:8]}{suffix}"
    temp_path = video_directory / f"{uuid4()}.tmp"
    bytes_written = 0
    try:
        with temp_path.open("wb") as target_file:
            while chunk := upload_file.file.read(1024 * 1024):
                bytes_written += len(chunk)
                if bytes_written > settings.max_upload_size_mb * 1024 * 1024:
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds maximum size")
                target_file.write(chunk)
        if settings.storage_backend.lower() == "s3":
            url = _persist_to_s3(StorageCategory.video, temp_path, final_filename, upload_file.content_type)
            prefix = settings.aws_s3_prefix.strip("/")
            storage_key = f"{prefix}/videos/{final_filename}" if prefix else f"videos/{final_filename}"
        else:
            url = _persist_to_local(StorageCategory.video, temp_path, final_filename)
            storage_key = f"videos/{final_filename}"
        return StorageResult(
            url=url,
            storage_key=storage_key,
            filename=final_filename,
            size_bytes=bytes_written,
            content_type=upload_file.content_type,
        )
    finally:
        temp_path.unlink(missing_ok=True)

def store_meeting_audio(upload_file: UploadFile) -> StorageResult:
    """Accept audio recordings or plain-text transcripts for local/dev workflows."""
    content_type = (upload_file.content_type or "").lower()
    filename = (upload_file.filename or "").lower()
    if content_type in ALLOWED_DOCUMENT_CONTENT_TYPES or filename.endswith((".txt", ".md")):
        # Normalize empty/odd browser mime for .txt uploads
        if not upload_file.content_type or upload_file.content_type == "application/octet-stream":
            upload_file.content_type = "text/plain"
        result = store_document_upload(upload_file)
        return StorageResult(
            url=result.url,
            storage_key=result.storage_key,
            filename=result.filename,
            size_bytes=result.size_bytes,
            content_type=result.content_type,
            duration_seconds=60.0,
        )
    if content_type.startswith("video/") or filename.endswith((".mp4", ".mov", ".mkv", ".avi", ".webm")):
        return store_video_upload(upload_file)
    return store_audio_upload(upload_file)


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
        key_prefix = settings.aws_s3_prefix.strip("/")
        storage_key = f"{key_prefix}/{StorageCategory.transcripts.value}/{final_filename}" if key_prefix else f"{StorageCategory.transcripts.value}/{final_filename}"
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
