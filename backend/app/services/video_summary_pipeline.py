from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.core.settings import get_settings

logger = logging.getLogger(__name__)
T = TypeVar("T")

AUDIO_SAMPLE_RATE = 16_000
AUDIO_CHANNELS = 1
CHUNK_SECONDS = 600
OVERLAP_SECONDS = 5
MAX_RETRIES = 2
CEREBRAS_MODEL_PREFERENCE = (
    "gpt-oss-120b",
    "zai-glm-4.7",
    "llama3.1-8b",
    "qwen-3-235b-a22b-instruct-2507",
)


class Decision(BaseModel):
    model_config = ConfigDict(extra="ignore")
    decision: str
    rationale: str | None = None


class ActionItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    task: str
    owner: str | None = None
    deadline: str | None = None
    priority: str = "medium"
    details: str | None = None


class KeyNote(BaseModel):
    model_config = ConfigDict(extra="ignore")
    note: str


class MeetingSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")
    summary: str = Field(min_length=1)
    decisions: list[Decision] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    key_notes: list[KeyNote] = Field(default_factory=list)
    risks: list[dict[str, Any]] = Field(default_factory=list)


class ChunkExtraction(MeetingSummary):
    pass


def _run(command: list[str], stage: str) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "unknown ffmpeg error").strip()
        raise RuntimeError(f"{stage} failed (exit {result.returncode}): {detail[-1200:]}")


def _binary_path(name: str) -> str:
    settings = get_settings()
    candidates: list[Path] = []
    if settings.ffmpeg_bin_dir:
        candidates.extend([Path(settings.ffmpeg_bin_dir) / f"{name}.exe", Path(settings.ffmpeg_bin_dir) / name])
    project_tools = Path(__file__).resolve().parents[3] / ".tools" / "ffmpeg"
    candidates.extend(project_tools.glob(f"*/bin/{name}.exe"))
    candidates.extend(project_tools.glob(f"*/bin/{name}"))
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    system_path = shutil.which(name)
    if system_path:
        return system_path
    raise RuntimeError(f"{name} is required but was not found. Install FFmpeg or set FFMPEG_BIN_DIR to its bin folder.")

def _duration(path: Path) -> float:
    result = subprocess.run(
        [_binary_path("ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Could not read audio duration: {(result.stderr or '').strip()[-1000:]}")
    try:
        value = float(result.stdout.strip())
    except ValueError as exc:
        raise RuntimeError("ffprobe returned an invalid audio duration") from exc
    if value <= 0:
        raise RuntimeError("Audio duration is zero; extraction produced no usable audio")
    return value


def _extract_audio(video_path: Path, output_path: Path) -> float:
    started = time.perf_counter()
    ffmpeg = _binary_path("ffmpeg")
    ffprobe = _binary_path("ffprobe")
    _run(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(video_path),
            "-vn", "-ac", str(AUDIO_CHANNELS), "-ar", str(AUDIO_SAMPLE_RATE),
            "-c:a", "pcm_s16le", str(output_path),
        ],
        "Audio extraction",
    )
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("Audio extraction completed without producing a usable audio file")
    probe = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate,channels", "-of", "json", str(output_path)],
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0:
        raise RuntimeError(f"Extracted audio validation failed: {(probe.stderr or '').strip()[-1000:]}")
    streams = json.loads(probe.stdout).get("streams", [])
    if not streams or int(streams[0].get("sample_rate", 0)) != AUDIO_SAMPLE_RATE or int(streams[0].get("channels", 0)) != AUDIO_CHANNELS:
        raise RuntimeError("Extracted audio is not 16kHz mono PCM audio")
    duration = _duration(output_path)
    logger.info("audio extraction completed in %.2fs: %.1fs", time.perf_counter() - started, duration)
    return duration


def _chunk_audio(audio_path: Path, duration: float, directory: Path) -> list[Path]:
    if duration <= 20 * 60:
        return [audio_path]
    started = time.perf_counter()
    chunk_count = max(1, int((duration + CHUNK_SECONDS - 1) // CHUNK_SECONDS))
    output_paths = [directory / f"chunk_{index:03d}.wav" for index in range(chunk_count)]
    filters: list[str] = []
    command = [_binary_path("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", str(audio_path), "-filter_complex"]
    for index in range(chunk_count):
        start = max(0, index * CHUNK_SECONDS - OVERLAP_SECONDS)
        end = min(duration, (index + 1) * CHUNK_SECONDS)
        filters.append(f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[chunk{index}]")
    command.append(";".join(filters))
    for index, output_path in enumerate(output_paths):
        command.extend(["-map", f"[chunk{index}]", "-c:a", "pcm_s16le", str(output_path)])
    # The segment muxer cannot express overlapping windows. This single ffmpeg
    # process creates the same 10-minute windows with a 5-second overlap without
    # looping re-encodes.
    _run(command, "Audio chunking")
    chunks = [chunk for chunk in output_paths if chunk.exists() and chunk.stat().st_size > 0]
    if len(chunks) != len(output_paths):
        raise RuntimeError("Audio chunking produced missing or empty chunks")
    logger.info("audio chunking completed in %.2fs: %d chunks (%ds overlap)", time.perf_counter() - started, len(chunks), OVERLAP_SECONDS)
    return chunks

def _retry(operation: Callable[[str], T], label: str) -> T:
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            return operation("" if attempt == 0 else " Return ONLY valid JSON, no markdown formatting, no explanation text.")
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                delay = 2**attempt
                logger.warning("%s failed (attempt %d/%d): %s; retrying in %ds", label, attempt + 1, MAX_RETRIES + 1, exc, delay)
                time.sleep(delay)
    raise RuntimeError(f"{label} failed after {MAX_RETRIES + 1} attempts: {last_error}") from last_error


def _groq_client() -> OpenAI:
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return OpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1")


def _cerebras_client() -> OpenAI:
    settings = get_settings()
    if not settings.cerebras_api_key:
        raise RuntimeError("CEREBRAS_API_KEY is not configured")
    return OpenAI(api_key=settings.cerebras_api_key, base_url="https://api.cerebras.ai/v1")


@lru_cache(maxsize=8)
def _resolve_cerebras_model(configured_model: str, api_key: str) -> str:
    """Resolve a configured model against the models available to this API key."""
    client = OpenAI(api_key=api_key, base_url="https://api.cerebras.ai/v1")
    try:
        response = client.models.list()
        available = {
            str(getattr(model, "id", "")).strip()
            for model in getattr(response, "data", [])
            if getattr(model, "id", None)
        }
    except Exception as exc:
        raise RuntimeError(
            "Could not query Cerebras models. Check CEREBRAS_API_KEY and network access."
        ) from exc

    requested = configured_model.strip()
    if requested and requested.lower() not in {"auto", "default"}:
        if requested in available:
            return requested
        logger.warning(
            "CEREBRAS_MODEL=%s is unavailable for this API key; selecting an available model",
            requested,
        )

    for model in CEREBRAS_MODEL_PREFERENCE:
        if model in available:
            logger.info("Using Cerebras model: %s", model)
            return model

    if available:
        selected = sorted(available)[0]
        logger.info("Using Cerebras model returned by account: %s", selected)
        return selected

    raise RuntimeError(
        "Cerebras returned no available models for this API key. "
        "Set CEREBRAS_MODEL to a model enabled for your account."
    )


def _cerebras_model() -> str:
    settings = get_settings()
    if not settings.cerebras_api_key:
        raise RuntimeError("CEREBRAS_API_KEY is not configured")
    return _resolve_cerebras_model(settings.cerebras_model, settings.cerebras_api_key)


def _transcribe_chunk(path: Path, index: int) -> tuple[int, str]:
    started = time.perf_counter()
    def call(_: str) -> str:
        client = _groq_client()
        with path.open("rb") as audio:
            response = client.audio.transcriptions.create(model=get_settings().groq_whisper_model, file=audio, response_format="json")
        text = str(getattr(response, "text", "") or "").strip()
        if not text:
            raise ValueError("transcription returned empty text")
        return text
    text = _retry(call, f"transcription chunk {index + 1}")
    logger.info("transcription chunk %d completed in %.2fs", index + 1, time.perf_counter() - started)
    return index, text


def _json_content(response: Any) -> dict[str, Any]:
    content = response.choices[0].message.content if response.choices else "{}"
    payload = json.loads(content or "{}")
    if not isinstance(payload, dict):
        raise ValueError("LLM response was not a JSON object")
    return payload


def _extract_chunk(text: str, index: int) -> tuple[int, ChunkExtraction]:
    started = time.perf_counter()
    instruction = (
        "Return JSON with exactly these conceptual fields: summary (string), decisions (array of {decision,rationale}), "
        "action_items (array of {task,owner,deadline,priority,details}), key_notes (array of {note}), risks (array). "
        "Extract only this transcript chunk; do not invent details."
    )
    def call(retry_suffix: str) -> ChunkExtraction:
        response = _cerebras_client().chat.completions.create(
            model=_cerebras_model(),
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": instruction + retry_suffix},
                {"role": "user", "content": text},
            ],
        )
        return ChunkExtraction.model_validate(_json_content(response))
    result = _retry(call, f"summary extraction chunk {index + 1}")
    logger.info("summary extraction chunk %d completed in %.2fs", index + 1, time.perf_counter() - started)
    return index, result


def _reduce(chunks: list[ChunkExtraction]) -> MeetingSummary:
    started = time.perf_counter()
    compact = [chunk.model_dump(exclude_none=True) for chunk in chunks]
    instruction = (
        "Merge these chunk JSON objects into one meeting result. Deduplicate decisions, action items, and key notes "
        "that repeat because of chunk overlap. Return only JSON with summary, decisions, action_items, key_notes, and risks."
    )
    def call(retry_suffix: str) -> MeetingSummary:
        response = _cerebras_client().chat.completions.create(
            model=_cerebras_model(),
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": instruction + retry_suffix},
                {"role": "user", "content": json.dumps(compact, ensure_ascii=False)},
            ],
        )
        return MeetingSummary.model_validate(_json_content(response))
    result = _retry(call, "summary reduce")
    logger.info("summary reduce completed in %.2fs", time.perf_counter() - started)
    return result



def _deduplicate(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in items:
        value = " ".join(str(item.get(key, "")).lower().split())
        if value and value not in seen:
            seen.add(value)
            unique.append(item)
    return unique
def process_meeting(file_path: str | os.PathLike[str]) -> dict[str, Any]:
    """Extract, transcribe, and summarize a meeting recording."""
    source = Path(file_path)
    if not source.exists() or source.stat().st_size == 0:
        raise FileNotFoundError(f"Meeting recording is missing or empty: {source}")
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="meeting-pipeline-") as temporary:
        directory = Path(temporary)
        audio_path = directory / "audio.wav"
        duration = _extract_audio(source, audio_path)
        chunks = _chunk_audio(audio_path, duration, directory)

        transcripts: list[str] = [""] * len(chunks)
        with ThreadPoolExecutor(max_workers=min(get_settings().pipeline_max_workers, len(chunks), 8)) as pool:
            futures = [pool.submit(_transcribe_chunk, chunk, index) for index, chunk in enumerate(chunks)]
            for future in as_completed(futures):
                index, text = future.result()
                transcripts[index] = text
        transcript = "\n\n".join(text for text in transcripts if text)
        if not transcript:
            raise RuntimeError("All transcription chunks returned empty text")

        extracted: list[ChunkExtraction | None] = [None] * len(transcripts)
        with ThreadPoolExecutor(max_workers=min(get_settings().pipeline_max_workers, len(transcripts), 8)) as pool:
            futures = [pool.submit(_extract_chunk, text, index) for index, text in enumerate(transcripts) if text]
            for future in as_completed(futures):
                index, result = future.result()
                extracted[index] = result
        final = _reduce([result for result in extracted if result is not None])

    result = final.model_dump(exclude_none=True)
    result["decisions"] = _deduplicate(result.get("decisions", []), "decision")
    result["action_items"] = _deduplicate(result.get("action_items", []), "task")
    result["key_notes"] = _deduplicate(result.get("key_notes", []), "note")
    result["transcript"] = transcript
    result["duration_seconds"] = duration
    logger.info("meeting pipeline completed in %.2fs", time.perf_counter() - started)
    return result
