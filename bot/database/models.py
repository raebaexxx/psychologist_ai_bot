import aiosqlite


async def ensure_user_exists(
    db: aiosqlite.Connection,
    user_id: int,
    username: str | None,
    first_name: str | None,
) -> None:
    await db.execute(
        """INSERT OR IGNORE INTO users (user_id, username, first_name)
           VALUES (?, ?, ?)""",
        (user_id, username, first_name),
    )
    await db.commit()


async def save_message(
    db: aiosqlite.Connection,
    user_id: int,
    role: str,
    content: str,
    message_type: str = "text",
) -> None:
    await db.execute(
        """INSERT INTO dialogues (user_id, role, content, message_type)
           VALUES (?, ?, ?, ?)""",
        (user_id, role, content, message_type),
    )
    await db.commit()


async def get_recent_history(
    db: aiosqlite.Connection,
    user_id: int,
    limit: int = 20,
) -> list[dict]:
    cursor = await db.execute(
        """SELECT role, content FROM dialogues
           WHERE user_id = ?
           ORDER BY id DESC LIMIT ?""",
        (user_id, limit),
    )
    rows = await cursor.fetchall()
    return [{"role": row[0], "content": row[1]} for row in reversed(rows)]


async def get_diary_entries(
    db: aiosqlite.Connection,
    user_id: int,
    days: int | None = None,
) -> list[dict]:
    query = """SELECT content, created_at FROM dialogues
               WHERE user_id = ? AND message_type = 'voice' AND role = 'user'
               ORDER BY id DESC"""
    params = [user_id]
    if days:
        query = """SELECT content, created_at FROM dialogues
                   WHERE user_id = ? AND message_type = 'voice' AND role = 'user'
                   AND created_at >= datetime('now', ?)
                   ORDER BY id DESC"""
        params.append(f"-{days} days")
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    return [{"content": row[0], "date": row[1]} for row in rows]


async def get_stats(
    db: aiosqlite.Connection,
    user_id: int,
) -> dict:
    cursor = await db.execute(
        """SELECT COUNT(*), COUNT(DISTINCT date(created_at))
           FROM dialogues WHERE user_id = ?""",
        (user_id,),
    )
    total, days_active = await cursor.fetchone()

    cursor = await db.execute(
        """SELECT message_type, COUNT(*) FROM dialogues
           WHERE user_id = ? GROUP BY message_type""",
        (user_id,),
    )
    by_type = dict(await cursor.fetchall())

    return {"total": total, "days_active": days_active, "by_type": by_type}


async def add_reminder(
    db: aiosqlite.Connection,
    user_id: int,
    text: str,
    cron: str,
) -> int:
    cursor = await db.execute(
        """INSERT INTO reminders (user_id, text, cron) VALUES (?, ?, ?)""",
        (user_id, text, cron),
    )
    await db.commit()
    return cursor.lastrowid


async def get_reminders(
    db: aiosqlite.Connection,
    user_id: int,
) -> list[dict]:
    cursor = await db.execute(
        """SELECT id, text, cron, is_active FROM reminders
           WHERE user_id = ? AND is_active = 1 ORDER BY id""",
        (user_id,),
    )
    rows = await cursor.fetchall()
    return [
        {"id": r[0], "text": r[1], "cron": r[2], "active": r[3]}
        for r in rows
    ]


async def cancel_reminder(
    db: aiosqlite.Connection,
    user_id: int,
    reminder_id: int,
) -> bool:
    cursor = await db.execute(
        """UPDATE reminders SET is_active = 0
           WHERE id = ? AND user_id = ?""",
        (reminder_id, user_id),
    )
    await db.commit()
    return cursor.rowcount > 0


async def get_all_active_reminders(db: aiosqlite.Connection) -> list[dict]:
    cursor = await db.execute(
        """SELECT id, user_id, text, cron FROM reminders WHERE is_active = 1""",
    )
    rows = await cursor.fetchall()
    return [
        {"id": r[0], "user_id": r[1], "text": r[2], "cron": r[3]}
        for r in rows
    ]


async def start_session(
    db: aiosqlite.Connection,
    user_id: int,
) -> int:
    await db.execute(
        """UPDATE sessions SET status = 'ended', ended_at = datetime('now')
           WHERE user_id = ? AND status = 'active'""",
        (user_id,),
    )
    cursor = await db.execute(
        """INSERT INTO sessions (user_id, status) VALUES (?, 'active')""",
        (user_id,),
    )
    await db.commit()
    return cursor.lastrowid


async def end_session(
    db: aiosqlite.Connection,
    user_id: int,
    summary: str | None = None,
) -> bool:
    cursor = await db.execute(
        """UPDATE sessions SET status = 'ended', ended_at = datetime('now'),
           summary = COALESCE(?, summary) WHERE user_id = ? AND status = 'active'""",
        (summary, user_id),
    )
    await db.commit()
    return cursor.rowcount > 0


async def has_active_session(
    db: aiosqlite.Connection,
    user_id: int,
) -> bool:
    cursor = await db.execute(
        """SELECT id FROM sessions WHERE user_id = ? AND status = 'active'""",
        (user_id,),
    )
    return await cursor.fetchone() is not None
