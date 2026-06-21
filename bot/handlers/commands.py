from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.prompts.therapist import get_system_prompt, save_custom_prompt, reset_prompt

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я твой личный психолог-терапевт.\n\n"
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
        "🎤 **Голосовые сообщения**\n"
        "Отправь голосовое — я расшифрую его, проанализирую и пришлю:\n"
        "• ответ психолога\n"
        "• .md файл с полной расшифровкой для твоего дневника\n\n"
        "💬 **Текстовые сообщения**\n"
        "Просто напиши мне — я отвечу как психолог-терапевт\n\n"
        "🔒 Всё конфиденциально\n\n"
        "📝 **Промпт:**\n"
        "/prompt — показать текущий промпт\n"
        "/setprompt <текст> — установить свой промпт\n"
        "/resetprompt — сбросить на дефолтный"
    )


@router.message(Command("prompt"))
async def cmd_prompt(message: Message) -> None:
    prompt = get_system_prompt()
    await message.answer(
        f"📝 **Текущий промпт:**\n\n{prompt[:3000]}"
    )


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


@router.message(F.document)
async def handle_prompt_file(message: Message) -> None:
    if not message.document.file_name.endswith(".txt"):
        return

    file = await message.bot.get_file(message.document.file_id)
    content = await message.bot.download_file(file.file_path)
    text = content.read().decode("utf-8")
    save_custom_prompt(text)
    await message.answer(f"✅ Промпт загружен из файла `{message.document.file_name}`")
