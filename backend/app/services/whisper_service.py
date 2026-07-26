from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any

from app.core.settings import get_settings

logger = logging.getLogger(__name__)
_model: Any | None = None
_model_lock = Lock()

@dataclass(frozen=True)
class WhisperTranscriptionResult:
    text: str
    language: str | None
    duration_seconds: float | None
    confidence_score: float | None
    model_name: str

def get_model() -> Any:
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                try:
                    from faster_whisper import WhisperModel
                except ImportError as exc:
                    raise RuntimeError("faster-whisper is required. Install backend requirements before processing meetings.") from exc
                settings = get_settings()
                logger.info("Loading Faster-Whisper model: %s", settings.whisper_model_name)
                _model = WhisperModel(settings.whisper_model_name, device=settings.whisper_device, compute_type=settings.whisper_compute_type)
    return _model

def preload_model() -> None:
    get_model()

def transcribe_audio(audio_path: Path) -> WhisperTranscriptionResult:
    settings = get_settings()
    segments, info = get_model().transcribe(str(audio_path), language=settings.whisper_language, vad_filter=True)
    texts: list[str] = []
    confidences: list[float] = []
    for segment in segments:
        text = (segment.text or "").strip()
        if text:
            texts.append(text)
        avg_logprob = getattr(segment, "avg_logprob", None)
        if avg_logprob is not None:
            confidences.append(float(avg_logprob))
    transcript = " ".join(texts).strip()
    if not transcript:
        raise RuntimeError("Faster-Whisper returned an empty transcript")
    return WhisperTranscriptionResult(transcript, getattr(info, "language", None), float(getattr(info, "duration", 0) or 0) or None, round(sum(confidences) / len(confidences), 4) if confidences else None, f"faster-whisper:{settings.whisper_model_name}")
