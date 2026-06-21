from pathlib import Path

from bot.config import settings

DEFAULT_PROMPT_PATH = Path(__file__).parent / "default_therapist.txt"
CUSTOM_PROMPT_DATA = Path("data") / "custom_prompt.txt"
PRESETS_DIR = Path(__file__).parent / "presets"
SELECTED_PRESET = Path("data") / "selected_preset.txt"

PRESET_DESCRIPTIONS = {
    "default": "Классический психолог-терапевт",
    "cbt": "Когнитивно-поведенческая терапия (КПТ)",
    "gestalt": "Гештальт-терапия",
    "jungian": "Юнгианский анализ",
    "coach": "Коучинг",
}


def list_presets() -> list[tuple[str, str]]:
    presets = [("default", PRESET_DESCRIPTIONS["default"])]
    for f in sorted(PRESETS_DIR.glob("*.txt")):
        name = f.stem
        desc = PRESET_DESCRIPTIONS.get(name, name)
        presets.append((name, desc))
    return presets


def select_preset(name: str) -> bool:
    if name == "default":
        SELECTED_PRESET.unlink(missing_ok=True)
        return True
    preset_file = PRESETS_DIR / f"{name}.txt"
    if not preset_file.exists():
        return False
    SELECTED_PRESET.parent.mkdir(parents=True, exist_ok=True)
    SELECTED_PRESET.write_text(name, encoding="utf-8")
    return True


def get_active_preset_name() -> str:
    if SELECTED_PRESET.exists():
        return SELECTED_PRESET.read_text(encoding="utf-8").strip()
    return "default"


def load_prompt() -> str:
    preset = get_active_preset_name()
    if preset != "default":
        preset_file = PRESETS_DIR / f"{preset}.txt"
        if preset_file.exists():
            return preset_file.read_text(encoding="utf-8")

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
    SELECTED_PRESET.unlink(missing_ok=True)


def get_system_prompt() -> str:
    return load_prompt()
