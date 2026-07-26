# Phase 10 - AI Meeting Analysis

This phase adds the LLM-based analysis stage after transcription and cleanup.

## Input
- Clean transcript text from the previous pipeline steps

## Output
- Executive summary
- Decisions
- Action items
- Risks
- Analysis payload metadata

## Storage
- Stores analysis in `meeting_summaries`
- Stores request/response metadata in `ai_logs`
- Exposes a read API for the saved analysis

## API
- `GET /api/v1/meetings/{meeting_id}/analysis`

## Notes
- The worker uses OpenAI when `OPENAI_API_KEY` is available
- A local fallback heuristic is used when the key or SDK is unavailable so the pipeline still completes in development

## Optimized video pipeline

When `GROQ_API_KEY` and `CEREBRAS_API_KEY` are configured, the worker uses `process_meeting(file_path)` from `app.services.video_summary_pipeline`:

- ffmpeg validates extracted PCM audio at 16kHz mono and rejects failed or empty output;
- recordings longer than 20 minutes are split into 10-minute windows with a 5-second overlap in one ffmpeg process;
- Groq Whisper transcription and Cerebras chunk extraction run concurrently, preserving source order;
- a final Cerebras reduce call deduplicates overlap and returns `summary`, `decisions`, `action_items`, `key_notes`, and `risks`;
- API calls retry twice with exponential backoff and Pydantic validation before acceptance.

Set `GROQ_API_KEY`, `CEREBRAS_API_KEY`, and optionally `PIPELINE_MAX_WORKERS` in `backend/.env`. If FFmpeg is installed outside PATH, set `FFMPEG_BIN_DIR` to its `bin` directory; the pipeline also searches `.tools/ffmpeg/*/bin`.