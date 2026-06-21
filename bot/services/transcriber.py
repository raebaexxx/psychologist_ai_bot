import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel

_model: WhisperModel | None = None


def init_transcriber(model_size: str = "medium", device: str = "auto") -> None:
    global _model
    _model = WhisperModel(model_size, device=device, compute_type="int8")


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
