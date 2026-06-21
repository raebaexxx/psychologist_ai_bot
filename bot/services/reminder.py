import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot

from bot.database.db import get_db
from bot.database.models import get_all_active_reminders

logger = logging.getLogger(__name__)

_CHECK_INTERVAL = 30


async def reminder_daemon(bot: Bot) -> None:
    while True:
        try:
            db = await get_db()
            reminders = await get_all_active_reminders(db)
            now = datetime.now()

            for r in reminders:
                parts = r["cron"].strip().lower().split()
                if len(parts) < 2:
                    continue

                interval = parts[0]
                time_str = parts[1]

                target_hour, target_min = map(int, time_str.split(":"))

                if interval == "daily":
                    if now.hour == target_hour and now.minute == target_min:
                        try:
                            await bot.send_message(
                                r["user_id"],
                                f"⏰ **Напоминание:** {r['text']}",
                            )
                            logger.info("Sent reminder %d to user %d", r["id"], r["user_id"])
                        except Exception as e:
                            logger.warning("Failed reminder %d: %s", r["id"], e)

            await asyncio.sleep(_CHECK_INTERVAL)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Reminder daemon error: %s", e)
            await asyncio.sleep(_CHECK_INTERVAL)
