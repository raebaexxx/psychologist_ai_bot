import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.config import settings
from bot.database.db import init_db
from bot.handlers import commands, voice, text
from bot.services.transcriber import init_transcriber

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("aiogram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def on_startup() -> None:
    logger.info("Initializing database...")
    await init_db(settings.database_path)

    logger.info("Loading Whisper model (%s)...", settings.whisper_model_size)
    init_transcriber(settings.whisper_model_size)

    logger.info("Bot is ready!")


async def on_shutdown() -> None:
    logger.info("Shutting down...")


async def main() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="Markdown"),
    )
    dp = Dispatcher()

    dp.include_router(commands.router)
    dp.include_router(voice.router)
    dp.include_router(text.router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
