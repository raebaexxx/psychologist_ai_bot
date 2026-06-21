from pathlib import Path

from bot.config import settings

DEFAULT_PROMPT_PATH = Path(__file__).parent / "default_therapist.txt"
CUSTOM_PROMPT_DATA = Path("data") / "custom_prompt.txt"


def load_prompt() -> str:
    if CUSTOM_PROMPT_DATA.exists():
        return CUSTOM_PROMPT_DATA.read_text(encoding="utf-8")

    if settings.custom_prompt_path:
        custom = Path(settings.custom_prompt_path)
        if custom.exists():
            return custom.read_text(encoding="utf-8")

    return DEFAULT_PROMPT_PATH.read_text(encoding="utf-8")


def save_custom_prompt(text: str) -> None:
    CUSTOM_PROMPT_DATA.parent.mkdir(parents=True, exist_ok=True)
    CUSTOM_PROMPT_DATA.write_text(text, encoding="utf-8")


def reset_prompt() -> None:
    CUSTOM_PROMPT_DATA.unlink(missing_ok=True)


def get_system_prompt() -> str:
    return load_prompt()
