import io
import zipfile
from datetime import datetime

from bot.database.db import get_db
from bot.database.models import get_diary_entries


async def export_diary(user_id: int, days: int | None = None) -> io.BytesIO | None:
    db = await get_db()
    entries = await get_diary_entries(db, user_id, days)
    if not entries:
        return None

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, entry in enumerate(entries, 1):
            date_str = entry["date"][:10] if entry["date"] else "unknown"
            content = entry["content"]

            md = f"# Diary Entry {i}\n\nDate: {date_str}\n\n{content}\n"
            zf.writestr(f"entry_{i:03d}_{date_str}.md", md.encode("utf-8"))

    buf.seek(0)
    return buf
