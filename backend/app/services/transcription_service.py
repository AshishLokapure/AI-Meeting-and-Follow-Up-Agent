from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.models import Meeting, MeetingTranscript
from app.models.enums import MeetingStatus
from app.utils import store_transcript_text


class TranscriptResult:
    def __init__(
        self,
        transcript_text: str,
        language: str | None,
        confidence_score: float | None,
        word_count: int,
        transcript_storage_url: str | None,
        transcription_model: str,
    ) -> None:
        self.transcript_text = transcript_text
        self.language = language
        self.confidence_score = confidence_score
        self.word_count = word_count
        self.transcript_storage_url = transcript_storage_url
        self.transcription_model = transcription_model


class TranscriptionService:
    @staticmethod
    def _resolve_local_audio_path(meeting: Meeting) -> Path:
        settings = get_settings()
        if not meeting.recording_url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Meeting recording is missing")
        relative_path = meeting.recording_url.lstrip("/")
        local_path = Path(settings.uploads_root) / Path(relative_path).relative_to("uploads")
        if not local_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording file not found")
        return local_path

    @staticmethod
    def _download_s3_audio(meeting: Meeting) -> Path:
        settings = get_settings()
        storage_key = (meeting.source_metadata or {}).get("storage_key")
        if not settings.aws_bucket_name or not storage_key:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="S3 recording metadata is incomplete")

        try:
            import boto3
        except ImportError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="S3 support is unavailable") from exc

        suffix = Path(meeting.recording_filename or "recording.bin").suffix or ".bin"
        temp_file = NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.close()
        s3_client = boto3.client("s3", region_name=settings.aws_region)
        s3_client.download_file(settings.aws_bucket_name, storage_key, temp_file.name)
        return Path(temp_file.name)

    @classmethod
    def resolve_audio_path(cls, meeting: Meeting) -> tuple[Path, bool]:
        storage_backend = (meeting.source_metadata or {}).get("storage_backend", get_settings().storage_backend).lower()
        if storage_backend == "s3":
            return cls._download_s3_audio(meeting), True
        return cls._resolve_local_audio_path(meeting), False

    @staticmethod
    def _load_whisper_model() -> tuple[Any, str]:
        settings = get_settings()
        try:
            import whisper
        except ImportError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Whisper is not installed in the current environment",
            ) from exc

        model = whisper.load_model(settings.whisper_model_name)
        return model, settings.whisper_model_name

    @staticmethod
    def _calculate_confidence(result: dict[str, Any]) -> float | None:
        segments = result.get("segments") or []
        if not segments:
            return None
        confidences = [segment.get("avg_logprob") for segment in segments if segment.get("avg_logprob") is not None]
        if not confidences:
            return None
        return round(sum(confidences) / len(confidences), 4)

    @classmethod
    def transcribe_meeting(cls, db: Session, meeting: Meeting) -> TranscriptResult:
        audio_path, should_cleanup = cls.resolve_audio_path(meeting)
        model, model_name = cls._load_whisper_model()
        try:
            whisper_result = model.transcribe(
                str(audio_path),
                language=get_settings().whisper_language,
                fp16=False,
            )
        finally:
            if should_cleanup:
                audio_path.unlink(missing_ok=True)

        transcript_text = (whisper_result.get("text") or "").strip()
        if not transcript_text:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Whisper returned an empty transcript")

        transcript_storage = store_transcript_text(meeting.id, transcript_text)
        transcript = db.scalar(select(MeetingTranscript).where(MeetingTranscript.meeting_id == meeting.id))
        if transcript is None:
            transcript = MeetingTranscript(meeting_id=meeting.id, transcript_text=transcript_text)
            db.add(transcript)

        transcript.transcript_text = transcript_text
        transcript.cleaned_text = transcript_text
        transcript.language = whisper_result.get("language")
        transcript.confidence_score = cls._calculate_confidence(whisper_result)
        transcript.source_uri = meeting.recording_url
        transcript.word_count = len(transcript_text.split())
        transcript.transcription_model = model_name
        transcript.duration_seconds = float(meeting.duration_seconds or 0)
        transcript.transcript_format = "text/plain"
        transcript.transcript_storage_url = transcript_storage.url

        meeting.status = MeetingStatus.transcribed.value
        return TranscriptResult(
            transcript_text=transcript_text,
            language=transcript.language,
            confidence_score=transcript.confidence_score,
            word_count=transcript.word_count or 0,
            transcript_storage_url=transcript_storage.url,
            transcription_model=model_name,
        )
