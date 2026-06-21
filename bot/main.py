import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.config import settings
from bot.database.db import init_db
from bot.handlers import commands, voice, text
from bot.services.transcriber import init_transcriber_async
from bot.services.reminder import reminder_daemon

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
logging.getLogger("ctranslate2").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    logger.info("Initializing database...")
    await init_db(settings.database_path)

    logger.info("Starting reminder daemon...")
    asyncio.create_task(reminder_daemon(bot))

    logger.info("Loading Whisper model in background...")
    asyncio.create_task(init_transcriber_async(settings.whisper_model_size))


async def on_shutdown() -> None:
    logger.info("Shutting down...")


def _make_session():
    from aiogram.client.session.aiohttp import AiohttpSession

    proxy = os.environ.get("all_proxy") or os.environ.get("ALL_PROXY") or ""
    if proxy:
        proxy = proxy.replace("socks://", "socks5://")
        logger.info("Using proxy: %s", proxy)
        return AiohttpSession(proxy=proxy)
    return AiohttpSession()


async def main() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="Markdown"),
        session=_make_session(),
    )
    dp = Dispatcher()

    dp.include_router(commands.router)
    dp.include_router(voice.router)
    dp.include_router(text.router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        logger.info("Bot started! The model will load in background.")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
