# Phase 6 - File Storage

This phase formalizes file persistence for the backend.

## Local layout
- `uploads/audio/`
- `uploads/transcripts/`
- `uploads/documents/`

## AWS layout
- S3 bucket stores files under category prefixes
- The backend generates a URL and stores it in the database

## Notes
- Storage defaults to local filesystem
- S3 can be enabled with `STORAGE_BACKEND=s3`
- The same helper is reused for audio, transcript, and document artifacts
