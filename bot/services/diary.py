import tempfile
from datetime import datetime
from pathlib import Path


def generate_diary_md(
    transcript: str,
    analysis: str,
    language: str,
    user_name: str = "User",
) -> Path:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"""# Diary Entry — {now}

---

## Original Message (Transcript)

> *Language detected: {language}*

{transcript}

---

## Therapist Reflection

{analysis}

---

*Recorded on {now}*
"""

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8",
    )
    tmp.write(content)
    path = Path(tmp.name)
    tmp.close()
    return path
