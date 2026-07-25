# Phase 2 - Database Design

This phase defines the complete relational schema before API work begins.

## Core tables
- `users`
- `meetings`
- `meeting_participants`
- `meeting_transcripts`
- `meeting_summaries`
- `tasks`
- `task_activities`
- `notifications`
- `reminder_logs`
- `ai_logs`
- `system_logs`

## Relationship map
- `users` own many `meetings`
- `meetings` contain many `tasks`
- `tasks` generate many `notifications`
- `meetings` have participant, transcript, and summary records
- `tasks`, `notifications`, and logs are linked for traceability

## Design notes
- UUID primary keys across the schema
- Timestamps on every table
- PostgreSQL JSONB for flexible structured payloads
- Cascading deletes where child records should not outlive the parent
- Nullable foreign keys for optional assignees and recipients
