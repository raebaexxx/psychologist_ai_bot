import asyncio
import logging
import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

_model: WhisperModel | None = None
_loading = False
_ready = asyncio.Event()

CACHE_HOME = Path.home() / ".cache" / "huggingface" / "hub"


def _find_model_path(model_size: str) -> Path | None:
    repo_dir = CACHE_HOME / f"models--Systran--faster-whisper-{model_size}"
    refs_file = repo_dir / "refs" / "main"
    if not refs_file.exists():
        return None
    revision = refs_file.read_text().strip()
    snapshot = repo_dir / "snapshots" / revision
    return snapshot if snapshot.exists() else None


def is_ready() -> bool:
    return _model is not None


async def wait_ready(timeout: float | None = None) -> bool:
    try:
        await asyncio.wait_for(_ready.wait(), timeout=timeout)
        return True
    except asyncio.TimeoutError:
        return False


async def init_transcriber_async(model_size: str = "medium", device: str = "auto") -> None:
    global _model, _loading

    if _loading or is_ready():
        return

    _loading = True
    logger.info("Loading Whisper model (%s)...", model_size)

    model_path = _find_model_path(model_size)
    if model_path is None:
        logger.error(
            "Whisper model not found in cache.\n"
            "Run this to download:\n"
            "  uv run python scripts/download_model.py %s",
            model_size,
        )
        _loading = False
        return

    def _load():
        global _model
        _model = WhisperModel(str(model_path), device=device, compute_type="int8")

    await asyncio.to_thread(_load)
    _ready.set()
    _loading = False
    logger.info("Whisper model ready!")


async def transcribe_voice(ogg_path: str | Path) -> str:
    if _model is None:
        raise RuntimeError("Transcriber not initialized")

    def _run():
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(ogg_path),
                    "-ar", "16000", "-ac", "1",
                    "-sample_fmt", "s16", wav_path,
                ],
                capture_output=True, check=True,
            )
            segments, info = _model.transcribe(wav_path, beam_size=5)
            text_parts = [seg.text for seg in segments]
            return info.language, " ".join(text_parts)
        finally:
            Path(wav_path).unlink(missing_ok=True)

    return await asyncio.to_thread(_run)
