from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Meeting, MeetingTranscript

FILLER_PHRASES = [
    "um",
    "uh",
    "hmm",
    "okay",
    "ok",
    "basically",
    "actually",
    "correct",
]
SPEAKER_PREFIX_PATTERN = re.compile(r"^(speaker\s*\d+|speaker|host|participant|moderator)\s*[:\-]\s*", re.IGNORECASE)
MULTI_SPACE_PATTERN = re.compile(r"[ \t]{2,}")
MULTI_NEWLINE_PATTERN = re.compile(r"\n{3,}")
SENTENCE_BOUNDARY_PATTERN = re.compile(r"([.!?])\s+")
FILLER_PATTERN = re.compile(r"\b(?:" + "|".join(re.escape(word) for word in FILLER_PHRASES) + r")\b[,.!?;:]*", re.IGNORECASE)


@dataclass(frozen=True)
class TranscriptCleanupResult:
    cleaned_text: str
    removed_fillers: int
    paragraph_count: int


class TranscriptProcessingService:
    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = MULTI_SPACE_PATTERN.sub(" ", text)
        text = MULTI_NEWLINE_PATTERN.sub("\n\n", text)
        return text.strip()

    @staticmethod
    def _remove_speaker_labels(lines: Iterable[str]) -> list[str]:
        cleaned_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            cleaned_lines.append(stripped)
        return cleaned_lines

    @classmethod
    def clean_text(cls, transcript_text: str) -> TranscriptCleanupResult:
        normalized = cls._normalize_whitespace(transcript_text)
        lines = normalized.split("\n")
        lines = cls._remove_speaker_labels(lines)
        text = " ".join(lines)
        text = FILLER_PATTERN.sub("", text)
        text = MULTI_SPACE_PATTERN.sub(" ", text)
        text = re.sub(r"\s+([,.;!?])", r"\1", text)
        text = re.sub(r"([.!?])([A-Za-z])", r"\1 \2", text)
        text = text.strip()

        sentences = [sentence.strip() for sentence in SENTENCE_BOUNDARY_PATTERN.split(text) if sentence.strip()]
        rebuilt_sentences: list[str] = []
        buffer = ""
        for chunk in sentences:
            if len(chunk) == 1 and chunk in ".!?":
                buffer += chunk
                rebuilt_sentences.append(buffer.strip())
                buffer = ""
            else:
                if buffer:
                    rebuilt_sentences.append(buffer.strip())
                buffer = chunk
        if buffer:
            rebuilt_sentences.append(buffer.strip())

        if not rebuilt_sentences:
            rebuilt_sentences = [text] if text else []

        paragraphs: list[str] = []
        current_paragraph: list[str] = []
        for index, sentence in enumerate(rebuilt_sentences, start=1):
            current_paragraph.append(sentence)
            if len(current_paragraph) >= 3 or index == len(rebuilt_sentences):
                paragraphs.append(" ".join(current_paragraph).strip())
                current_paragraph = []

        cleaned_text = "\n\n".join(paragraphs).strip()
        removed_fillers = len(FILLER_PATTERN.findall(transcript_text))
        return TranscriptCleanupResult(
            cleaned_text=cleaned_text,
            removed_fillers=removed_fillers,
            paragraph_count=len(paragraphs),
        )

    @classmethod
    def clean_meeting_transcript(cls, db: Session, meeting: Meeting, raw_text: str) -> TranscriptCleanupResult:
        transcript = db.scalar(select(MeetingTranscript).where(MeetingTranscript.meeting_id == meeting.id))
        if transcript is None:
            transcript = MeetingTranscript(meeting_id=meeting.id, transcript_text=raw_text)
            db.add(transcript)

        result = cls.clean_text(raw_text)
        transcript.cleaned_text = result.cleaned_text
        transcript.transcript_text = raw_text
        return result
