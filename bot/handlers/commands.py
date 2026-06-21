import io

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile

from bot.database import models
from bot.database.db import get_db
from bot.prompts.therapist import (
    get_system_prompt,
    save_custom_prompt,
    reset_prompt,
    list_presets,
    select_preset as _select_preset,
    get_active_preset_name,
)
from bot.services.export import export_diary
from bot.services.mood import get_mood_chart, analyze_mood

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    preset = get_active_preset_name()
    await message.answer(
        f"Привет! Я твой личный психолог-терапевт.\n\n"
        f"🧠 Текущий подход: *{preset}*\n\n"
        "Я здесь, чтобы выслушать тебя. Ты можешь:\n"
        "🎤 Отправить голосовое сообщение — я расшифрую его и дам обратную связь\n"
        "💬 Написать текстом — я проанализирую и отвечу\n\n"
        "Всё, чем ты делишься, остаётся между нами.\n"
        "Я не ставлю диагнозы, но помогу разобраться в чувствах.\n\n"
        "/help — подробнее о возможностях"
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "🎤 **Голосовые сообщения** — расшифровка + анализ + .md\n"
        "💬 **Текстовые сообщения** — просто напиши мне\n\n"
        "🧠 **Терапевты:**\n"
        "/therapists — список подходов\n"
        "/select <имя> — выбрать подход\n\n"
        "📝 **Промпт:**\n"
        "/prompt — показать текущий промпт\n"
        "/setprompt — установить свой промпт\n"
        "/resetprompt — сбросить на дефолтный\n\n"
        "📊 **Дневник и статистика:**\n"
        "/export — скачать дневник (.zip)\n"
        "/stats — статистика диалогов\n"
        "/mood — график настроения\n\n"
        "🎯 **Сессии:**\n"
        "/session — начать сессию\n"
        "/endsession — завершить сессию\n\n"
        "⏰ **Напоминания:**\n"
        "/remind daily 9:00 Как ты себя чувствуешь?\n"
        "/reminds — список напоминаний\n"
        "/remind cancel 1 — удалить напоминание"
    )


@router.message(Command("therapists"))
async def cmd_therapists(message: Message) -> None:
    presets = list_presets()
    active = get_active_preset_name()
    lines = ["🧠 **Доступные терапевты:**\n"]
    for name, desc in presets:
        marker = "✅" if name == active else "•"
        lines.append(f"{marker} `{name}` — {desc}")
    lines.append(
        "\nВыбрать: `/select <имя>`\n"
        "Сбросить: `/resetprompt`"
    )
    await message.answer("\n".join(lines))


@router.message(Command("select"))
async def cmd_select(message: Message) -> None:
    name = message.text.removeprefix("/select").strip()
    if not name:
        presets = list_presets()
        names = ", ".join(f"`{n}`" for n, _ in presets)
        await message.answer(f"Укажи имя терапевта: {names}")
        return

    if _select_preset(name):
        await message.answer(f"✅ Выбран подход: *{name}*")
    else:
        await message.answer(f"❌ Терапевт `{name}` не найден.")


@router.message(Command("prompt"))
async def cmd_prompt(message: Message) -> None:
    prompt = get_system_prompt()
    await message.answer(f"📝 **Текущий промпт:**\n\n{prompt[:3000]}")


@router.message(Command("setprompt"))
async def cmd_setprompt(message: Message) -> None:
    text = message.text.removeprefix("/setprompt").strip()
    if not text:
        await message.answer(
            "Напиши текст промпта после команды:\n"
            "`/setprompt Ты — психолог, ...`\n\n"
            "Или отправь файл `.txt` с промптом."
        )
        return

    save_custom_prompt(text)
    await message.answer("✅ Промпт сохранён!")


@router.message(Command("resetprompt"))
async def cmd_resetprompt(message: Message) -> None:
    reset_prompt()
    await message.answer("✅ Промпт сброшен на дефолтный.")


@router.message(Command("export"))
async def cmd_export(message: Message) -> None:
    status = await message.answer("📦 Формирую архив дневника...")

    try:
        text = message.text.removeprefix("/export").strip()
        days = int(text) if text.isdigit() else None

        buf = await export_diary(message.from_user.id, days)
        if buf is None:
            await status.edit_text("📭 Нет записей для экспорта.")
            return

        filename = "diary_export.zip"
        if days:
            filename = f"diary_export_last_{days}_days.zip"

        await message.answer_document(
            BufferedInputFile(buf.getvalue(), filename=filename),
            caption="📔 Архив дневника",
        )
        await status.delete()
    except Exception as e:
        await status.edit_text("❌ Ошибка при создании архива.")
        raise


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    db = await get_db()
    stats = await models.get_stats(db, message.from_user.id)
    by_type = stats["by_type"]
    lines = [
        "📊 **Статистика:**\n",
        f"📝 Всего сообщений: *{stats['total']}*",
        f"📅 Дней активности: *{stats['days_active']}*",
        f"🎤 Голосовых: *{by_type.get('voice', 0)}*",
        f"💬 Текстовых: *{by_type.get('text', 0)}*",
    ]
    await message.answer("\n".join(lines))


@router.message(Command("mood"))
async def cmd_mood(message: Message) -> None:
    status = await message.answer("📊 Анализирую настроение...")
    try:
        db = await get_db()
        chart = await get_mood_chart(db, message.from_user.id, days=7)
        await message.answer(chart)
        await status.delete()
    except Exception:
        await status.edit_text("❌ Ошибка анализа.")


@router.message(Command("session"))
async def cmd_session(message: Message) -> None:
    db = await get_db()
    has_active = await models.has_active_session(db, message.from_user.id)
    if has_active:
        await message.answer(
            "🎯 Сессия уже активна. Заверши её:\n`/endsession`"
        )
        return

    await models.start_session(db, message.from_user.id)
    await message.answer(
        "🎯 **Сессия начата!**\n\n"
        "Я буду задавать более структурированные вопросы.\n"
        "Когда будешь готов завершить — напиши `/endsession`.\n"
        "Я подготовлю краткое резюме нашей сессии."
    )


@router.message(Command("endsession"))
async def cmd_endsession(message: Message) -> None:
    db = await get_db()
    has_active = await models.has_active_session(db, message.from_user.id)
    if not has_active:
        await message.answer("Нет активной сессии. Начни новую: `/session`")
        return

    history = await models.get_recent_history(db, message.from_user.id, limit=50)
    summary_prompt = (
        "Сделай краткое резюме этой терапевтической сессии (3-5 предложений):\n"
        "основные темы, ключевые инсайты, рекомендации."
    )
    from bot.services.openrouter import ask_therapist
    summary = await ask_therapist(summary_prompt, history)

    await models.end_session(db, message.from_user.id, summary)
    await message.answer(
        f"🎯 **Сессия завершена!**\n\n"
        f"📝 **Резюме сессии:**\n\n{summary}"
    )


@router.message(Command("remind"))
async def cmd_remind(message: Message) -> None:
    text = message.text.removeprefix("/remind").strip()

    parts = text.split(maxsplit=2)
    if not parts:
        await message.answer(
            "Формат: `/remind daily 9:00 Твой текст`\n"
            "Список: `/reminds`\n"
            "Удалить: `/remind cancel 1`"
        )
        return

    if parts[0] == "cancel" and len(parts) >= 2:
        db = await get_db()
        ok = await models.cancel_reminder(db, message.from_user.id, int(parts[1]))
        await message.answer("✅ Напоминание удалено." if ok else "❌ Не найдено.")
        return

    if len(parts) < 2:
        await message.answer("Формат: `/remind daily 9:00 Твой текст`")
        return

    interval = parts[0]
    time_part = parts[1]
    reminder_text = parts[2] if len(parts) > 2 else ""

    if interval not in ("daily",):
        await message.answer("Пока поддерживается только `daily`.")
        return

    try:
        hour, minute = map(int, time_part.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except ValueError:
        await message.answer("Неверный формат времени. Используй `HH:MM`.")
        return

    if not reminder_text:
        await message.answer("Напиши текст напоминания.")
        return

    db = await get_db()
    rid = await models.add_reminder(
        db, message.from_user.id, reminder_text, f"{interval} {time_part}",
    )
    await message.answer(
        f"✅ Напоминание создано (id: {rid})\n"
        f"⏰ Каждый день в {time_part}: *{reminder_text}*"
    )


@router.message(Command("reminds"))
async def cmd_reminds(message: Message) -> None:
    db = await get_db()
    reminders = await models.get_reminders(db, message.from_user.id)
    if not reminders:
        await message.answer("Нет активных напоминаний.")
        return

    lines = ["⏰ **Напоминания:**\n"]
    for r in reminders:
        lines.append(f"{r['id']}. ⏱ {r['cron']} — *{r['text']}*")
    lines.append("\nУдалить: `/remind cancel <id>`")
    await message.answer("\n".join(lines))


@router.message(F.document)
async def handle_prompt_file(message: Message) -> None:
    if not message.document.file_name.endswith(".txt"):
        return

    file = await message.bot.get_file(message.document.file_id)
    content = await message.bot.download_file(file.file_path)
    text = content.read().decode("utf-8")
    save_custom_prompt(text)
    await message.answer(f"✅ Промпт загружен из файла `{message.document.file_name}`")
