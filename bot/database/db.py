import aiosqlite
from pathlib import Path

DATABASE_PATH: Path | None = None


async def init_db(db_path: str) -> None:
    global DATABASE_PATH
    DATABASE_PATH = Path(db_path)
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(str(DATABASE_PATH)) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS dialogues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                cron TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                started_at TEXT DEFAULT (datetime('now')),
                ended_at TEXT,
                summary TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)
        await db.commit()


async def get_db() -> aiosqlite.Connection:
    if DATABASE_PATH is None:
        raise RuntimeError("Database not initialized")
    return await aiosqlite.connect(str(DATABASE_PATH))
