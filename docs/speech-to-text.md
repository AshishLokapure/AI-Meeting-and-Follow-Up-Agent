# Phase 8 - Speech-to-Text

This phase adds the Whisper transcription step to the background pipeline.

## Flow
- Worker loads the uploaded audio file
- Whisper generates a transcript in the background
- Transcript is saved to the database
- Transcript text is also stored under `uploads/transcripts` when local storage is enabled
- Meeting status becomes `transcribed`

## API
- `GET /api/v1/meetings/{meeting_id}/transcript`

## Notes
- Whisper runs only in the Celery worker, never in the request thread
- If Whisper is unavailable in the environment, the worker fails the job clearly
- S3 audio uploads are supported through the same worker path
