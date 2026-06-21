from aiogram import Router, F
from aiogram.types import Message

from bot.database import models
from bot.database.db import get_db
from bot.services.openrouter import ask_therapist

router = Router()


@router.message(F.text)
async def handle_text(message: Message) -> None:
    status_msg = await message.answer("💭 Думаю над ответом...")

    try:
        db = await get_db()
        await models.ensure_user_exists(
            db,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
        )

        await models.save_message(
            db, message.from_user.id, "user", message.text, "text",
        )

        history = await models.get_recent_history(db, message.from_user.id)
        analysis = await ask_therapist(message.text, history)

        await models.save_message(
            db, message.from_user.id, "assistant", analysis, "text",
        )

        await message.answer(analysis)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(
            "🤖 Произошла ошибка. Попробуй ещё раз.",
        )
        raise
