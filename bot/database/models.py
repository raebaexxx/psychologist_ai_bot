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
