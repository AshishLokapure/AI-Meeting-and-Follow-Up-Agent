# Phase 5 - Meeting Upload

This phase adds the recording upload entrypoint.

## API
- `POST /api/v1/meetings/upload`

## Validation
- Accepted formats: `mp3`, `mp4`, `wav`, `m4a`
- Maximum size is configurable with `MAX_UPLOAD_SIZE_MB`
- Maximum duration is configurable with `MAX_MEETING_DURATION_MINUTES`

## Storage
- Default storage backend is local filesystem under `uploads/meetings`
- Optional S3 storage is available when `STORAGE_BACKEND=s3`
- The meeting row is created with `status=uploaded`
