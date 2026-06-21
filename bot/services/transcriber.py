import logging
import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel
from huggingface_hub import snapshot_download

logger = logging.getLogger(__name__)

_model: WhisperModel | None = None

WHISPER_REPO = "Systran/faster-whisper-medium"


def init_transcriber(model_size: str = "medium", device: str = "auto") -> None:
    global _model

    repo_id = f"Systran/faster-whisper-{model_size}"
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"

    model_dir = cache_dir / f"models--{repo_id.replace('/', '--')}"
    if model_dir.exists():
        logger.info("Whisper model found in cache, loading...")
    else:
        logger.info("Downloading Whisper model (%s) from Hugging Face...", model_size)
        logger.info("Model size: ~1.5 GB, one-time download")
        snapshot_download(repo_id=repo_id)

    _model = WhisperModel(model_size, device=device, compute_type="int8")
    logger.info("Whisper model loaded successfully")


async def transcribe_voice(ogg_path: str | Path) -> str:
    if _model is None:
        raise RuntimeError("Transcriber not initialized")

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
        language = info.language
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text)

        full_text = " ".join(text_parts)
        return language, full_text
    finally:
        Path(wav_path).unlink(missing_ok=True)
