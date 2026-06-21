import aiohttp
from bot.config import settings
from bot.prompts.therapist import get_system_prompt

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def ask_therapist(
    user_message: str,
    history: list[dict] | None = None,
) -> str:
    messages = [{"role": "system", "content": get_system_prompt()}]

    if history:
        for msg in history:
            if msg["role"] in ("user", "assistant"):
                messages.append(msg)

    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/raebaexxx/psychologist_ai_bot",
    }

    payload = {
        "model": settings.openrouter_model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OPENROUTER_URL, json=payload, headers=headers) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(f"OpenRouter error {resp.status}: {error_text}")

            data = await resp.json()
            return data["choices"][0]["message"]["content"]
