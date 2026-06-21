import tempfile
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile

from bot.database import models
from bot.database.db import get_db
from bot.services.transcriber import transcribe_voice, wait_ready
from bot.services.openrouter import ask_therapist
from bot.services.diary import generate_diary_md

router = Router()


@router.message(F.voice)
async def handle_voice(message: Message) -> None:
    status_msg = await message.answer("🎤 Слышу тебя... расшифровываю...")

    try:
        ready = await wait_ready(timeout=180)
        if not ready:
            await status_msg.edit_text(
                "⏳ Модель распознавания ещё загружается. Подожди немного и попробуй снова."
            )
            return

        voice = message.voice
        file = await message.bot.get_file(voice.file_id)

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            ogg_path = Path(tmp.name)

        await message.bot.download_file(file.file_path, ogg_path)

        await status_msg.edit_text("📝 Расшифровываю аудио...")
        language, transcript = await transcribe_voice(ogg_path)
        ogg_path.unlink(missing_ok=True)

        db = await get_db()
        await models.ensure_user_exists(
            db,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
        )

        user_text = f"[Voice transcribed from {language}]: {transcript}"
        await models.save_message(db, message.from_user.id, "user", user_text, "voice")

        history = await models.get_recent_history(db, message.from_user.id)

        await status_msg.edit_text("💭 Думаю над ответом...")
        analysis = await ask_therapist(user_text, history)

        await models.save_message(
            db, message.from_user.id, "assistant", analysis, "text",
        )

        user_name = message.from_user.first_name or "User"
        md_path = generate_diary_md(transcript, analysis, language, user_name)

        with open(md_path, "rb") as f:
            md_data = f.read()
        md_path.unlink(missing_ok=True)

        await message.answer(
            f"📝 **Расшифровка** ({language}):\n\n{transcript}\n\n"
            f"---\n\n💬 **Ответ психолога:**\n\n{analysis}",
        )
        await message.answer_document(
            BufferedInputFile(md_data, filename="diary_entry.md"),
            caption="📔 Запись для дневника",
        )

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(
            "🤖 Произошла ошибка при обработке. Попробуй ещё раз позже.",
        )
        raise
