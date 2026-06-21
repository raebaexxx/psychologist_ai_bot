from pathlib import Path

from bot.config import settings

DEFAULT_PROMPT_PATH = Path(__file__).parent / "default_therapist.txt"


def load_prompt() -> str:
    if settings.custom_prompt_path:
        custom = Path(settings.custom_prompt_path)
        if custom.exists():
            return custom.read_text(encoding="utf-8")

    return DEFAULT_PROMPT_PATH.read_text(encoding="utf-8")


def get_system_prompt() -> str:
    return load_prompt()
