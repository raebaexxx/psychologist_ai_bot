from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

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
        "🔒 Всё конфиденциально"
    )
