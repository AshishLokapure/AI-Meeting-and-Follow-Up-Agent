# Phase 9 - Transcript Processing

This phase cleans raw Whisper output into a structured transcript.

## Cleaning rules
- Remove filler words like `hmm`, `okay`, `basically`, `actually`, and `correct`
- Improve grammar and punctuation heuristically
- Split content into paragraphs
- Strip speaker labels where present

## Storage
- Raw transcript stays in `transcript_text`
- Cleaned transcript is stored in `cleaned_text`
- The transcript file is written under `uploads/transcripts`

## Pipeline
- Whisper produces raw text
- Transcript cleaner normalizes the text
- Worker stores the cleaned output in the database
