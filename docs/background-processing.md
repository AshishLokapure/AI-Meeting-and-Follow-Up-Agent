# Phase 7 - Background Processing

This phase moves AI work out of the request cycle.

## Flow
- Upload request stores the file and creates the meeting
- API returns success immediately
- A background job record is created
- Celery picks up the job from Redis
- Worker transitions the meeting into processing

## Components
- Redis as the queue broker
- Celery as the worker runtime
- Background job table for observability and retries

## Notes
- No AI processing should happen inside the upload request
- The worker currently marks the meeting as `processing` and records job state
- Later phases can extend the worker to run transcription, analysis, and task extraction
