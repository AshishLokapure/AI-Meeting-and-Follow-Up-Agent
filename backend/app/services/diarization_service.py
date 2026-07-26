from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any

from app.core.settings import get_settings

logger = logging.getLogger(__name__)
_pipeline: Any | None = None
_pipeline_lock = Lock()

@dataclass(frozen=True)
class SpeakerSegment:
    speaker: str
    start: float
    end: float

def get_pipeline() -> Any:
    global _pipeline
    if _pipeline is None:
        with _pipeline_lock:
            if _pipeline is None:
                settings = get_settings()
                if not settings.hf_token:
                    raise RuntimeError("HF_TOKEN is required for speaker diarization")
                try:
                    from pyannote.audio import Pipeline
                except ImportError as exc:
                    raise RuntimeError("pyannote.audio is required for speaker diarization") from exc
                logger.info("Loading diarization pipeline: %s", settings.diarization_model)
                _pipeline = Pipeline.from_pretrained(settings.diarization_model, token=settings.hf_token)
    return _pipeline

def preload_pipeline() -> None:
    get_pipeline()

def diarize_audio(audio_path: Path) -> list[SpeakerSegment]:
    output = get_pipeline()(str(audio_path))
    annotation = getattr(output, "exclusive_speaker_diarization", None) or getattr(output, "speaker_diarization", output)
    segments: list[SpeakerSegment] = []
    for turn, _, speaker in annotation.itertracks(yield_label=True):
        segments.append(SpeakerSegment(str(speaker), float(turn.start), float(turn.end)))
    return segments

def merge_with_transcript(transcript_segments: list[Any], speaker_segments: list[SpeakerSegment]) -> tuple[str, list[dict[str, Any]]]:
    if not speaker_segments:
        return " ".join((getattr(item, "text", "") or "").strip() for item in transcript_segments).strip(), []
    speaker_names: dict[str, str] = {}
    labeled: list[dict[str, Any]] = []
    for item in transcript_segments:
        start = float(getattr(item, "start", 0) or 0)
        end = float(getattr(item, "end", start) or start)
        text = (getattr(item, "text", "") or "").strip()
        if not text:
            continue
        overlaps = [(max(0.0, min(end, turn.end) - max(start, turn.start)), turn) for turn in speaker_segments]
        overlaps = [(overlap, turn) for overlap, turn in overlaps if overlap > 0]
        selected = max(overlaps, key=lambda pair: pair[0])[1] if overlaps else min(speaker_segments, key=lambda turn: abs(turn.start - start))
        display_name = speaker_names.setdefault(selected.speaker, f"Speaker {len(speaker_names) + 1}")
        labeled.append({"speaker": display_name, "speaker_id": selected.speaker, "start": start, "end": end, "text": text})
    grouped: list[str] = []
    for item in labeled:
        line = f"{item['speaker']}: {item['text']}"
        if grouped and grouped[-1].startswith(f"{item['speaker']}:"):
            grouped[-1] += f" {item['text']}"
        else:
            grouped.append(line)
    return "\n".join(grouped), labeled
