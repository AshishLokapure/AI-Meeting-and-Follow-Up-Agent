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
