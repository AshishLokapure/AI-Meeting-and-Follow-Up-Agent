from __future__ import annotations

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from app.core.settings import get_settings

logger = logging.getLogger(__name__)
SAMPLE_RATE = 16_000
CHANNELS = 1

@dataclass(frozen=True)
class AudioConversionResult:
    path: Path
    duration_seconds: float
    sample_rate: int
    channels: int

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
    found = shutil.which(name)
    if found:
        return found
    raise RuntimeError(f"{name} is required but was not found. Set FFMPEG_BIN_DIR to the FFmpeg bin folder.")

def _probe_audio(path: Path) -> tuple[float, int, int]:
    result = subprocess.run([_binary_path("ffprobe"), "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate,channels:format=duration", "-of", "json", str(path)], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFprobe validation failed: {(result.stderr or '').strip()[-1000:]}")
    data = json.loads(result.stdout or "{}")
    streams = data.get("streams") or []
    duration = float((data.get("format") or {}).get("duration") or 0)
    if not streams or duration <= 0:
        raise RuntimeError("FFmpeg produced an empty audio file")
    sample_rate = int(streams[0].get("sample_rate") or 0)
    channels = int(streams[0].get("channels") or 0)
    if sample_rate != SAMPLE_RATE or channels != CHANNELS:
        raise RuntimeError(f"Audio validation failed: expected {SAMPLE_RATE}Hz mono, got {sample_rate}Hz/{channels} channels")
    return duration, sample_rate, channels

def convert_video_to_audio(video_path: Path, audio_path: Path | None = None) -> AudioConversionResult:
    video_path = Path(video_path)
    if not video_path.exists() or video_path.stat().st_size == 0:
        raise FileNotFoundError(f"Meeting video is missing or empty: {video_path}")
    if audio_path is None:
        audio_path = Path(get_settings().uploads_root) / "audio" / f"{video_path.stem}.wav"
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([_binary_path("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", str(video_path), "-vn", "-ar", str(SAMPLE_RATE), "-ac", str(CHANNELS), "-c:a", "pcm_s16le", str(audio_path)], capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "unknown FFmpeg error").strip()
        raise RuntimeError(f"Video-to-audio conversion failed: {detail[-1200:]}")
    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise RuntimeError("FFmpeg completed without producing a usable WAV file")
    duration, sample_rate, channels = _probe_audio(audio_path)
    logger.info("Converted %s to %s", video_path.name, audio_path)
    return AudioConversionResult(audio_path, duration, sample_rate, channels)
