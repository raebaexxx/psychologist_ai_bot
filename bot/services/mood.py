import aiosqlite

MOOD_EMOJI = {
    "positive": "😊",
    "neutral": "😐",
    "negative": "😢",
}

MOOD_BAR = {
    "positive": "🟢",
    "neutral": "🟡",
    "negative": "🔴",
}


async def analyze_mood(text: str) -> str:
    from bot.services.openrouter import ask_therapist

    result = await ask_therapist(
        f"Classify the sentiment of this text as ONLY one word: positive, neutral, or negative. Text: {text}",
    )
    result = result.strip().lower().rstrip(".")
    if result in MOOD_EMOJI:
        return result
    return "neutral"


async def get_mood_chart(db: aiosqlite.Connection, user_id: int, days: int = 7) -> str:
    cursor = await db.execute(
        """SELECT date(created_at) as day,
                  COUNT(*) as count
           FROM dialogues
           WHERE user_id = ? AND role = 'user'
             AND created_at >= datetime('now', ?)
           GROUP BY day ORDER BY day""",
        (user_id, f"-{days} days"),
    )
    rows = await cursor.fetchall()
    if not rows:
        return "Нет данных за этот период."

    from datetime import datetime, timedelta
    today = datetime.now().date()
    date_map = {row[0]: row[1] for row in rows}

    lines = [f"📊 **Активность за последние {days} дней:**\n"]
    for i in range(days - 1, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        label = day.strftime("%a")
        count = date_map.get(day_str, 0)
        bar = "█" * min(count, 20) + "░" * max(0, 5 - min(count, 5))
        lines.append(f"{label} {bar} {count}")

    return "\n".join(lines)
