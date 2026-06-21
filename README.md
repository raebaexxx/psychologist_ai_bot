# Psychologist AI Bot

Telegram-бот — личный психолог-терапевт. Принимает голосовые и текстовые сообщения, расшифровывает, анализирует через AI и даёт эмпатичный ответ психолога. К каждому голосовому сообщению прикладывает `.md` файл с полной расшифровкой для личного дневника.

## Возможности

- **🎤 Голосовые сообщения** — расшифровка через faster-whisper (бесплатно, локально), анализ через OpenRouter, ответ психолога + `.md` файл с расшифровкой
- **💬 Текстовые сообщения** — анализ и ответ психолога
- **📔 Дневник** — к каждому голосовому приходит `.md` файл с полной расшифровкой и рефлексией терапевта (можно копировать в Obsidian / любой дневник)
- **🧠 Контекст** — бот помнит историю диалога (хранится в SQLite)
- **🔒 Конфиденциально** — всё хранится локально, твои данные не уходят третьим лицам (кроме OpenRouter)

## Технологии

| Компонент | |
|---|---|
| Bot Framework | aiogram 3.29 |
| Распознавание речи | faster-whisper (medium, локально) |
| AI | OpenRouter (бесплатные модели, `openrouter/free`) |
| База данных | SQLite |
| Пакетный менеджер | uv |
| Аудио-конвертер | ffmpeg |

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/raebaexxx/psychologist_ai_bot.git
cd psychologist_ai_bot
```

### 2. Настроить `.env`

```bash
cp .env .env.example  # для сохранности
nano .env
```

```
BOT_TOKEN=токен_от_BotFather
OPENROUTER_API_KEY=твой_ключ_openrouter
OPENROUTER_MODEL=openrouter/free
WHISPER_MODEL_SIZE=medium
DATABASE_PATH=data/diary.db
CUSTOM_PROMPT_PATH=                    # оставить пустым для дефолтного промпта
```

- **BOT_TOKEN** — получить у [@BotFather](https://t.me/BotFather)
- **OPENROUTER_API_KEY** — зарегистрироваться на [OpenRouter](https://openrouter.ai/), создать ключ (бесплатно, без карты)
- **CUSTOM_PROMPT_PATH** — если хочешь свой системный промпт, укажи путь к `.txt` файлу

### 3. Установить зависимости

```bash
uv sync
```

### 4. Убедиться, что ffmpeg установлен

```bash
# Linux (Debian/Ubuntu)
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

### 5. Запустить

```bash
uv run python -m bot.main
```

При первом запуске faster-whisper скачает модель `medium` (~1.5 ГБ) — это одноразово.

## Системный промпт

Промпт, задающий роль психолога, лежит в `bot/prompts/default_therapist.txt`. Ты можешь:

- Отредактировать его напрямую — под свой стиль терапии
- Создать свой `.txt` файл и указать путь в `CUSTOM_PROMPT_PATH` в `.env`

## Структура проекта

```
psychologist_ai_bot/
├── bot/
│   ├── main.py              # точка входа
│   ├── config.py            # настройки из .env
│   ├── handlers/
│   │   ├── commands.py      # /start, /help
│   │   ├── voice.py         # голосовые сообщения
│   │   └── text.py          # текстовые сообщения
│   ├── services/
│   │   ├── transcriber.py   # faster-whisper + ffmpeg
│   │   ├── openrouter.py    # OpenRouter API
│   │   └── diary.py         # генератор .md
│   ├── database/
│   │   ├── db.py            # SQLite
│   │   └── models.py        # CRUD
│   └── prompts/
│       ├── therapist.py     # загрузчик промпта
│       └── default_therapist.txt
├── .env
├── pyproject.toml
└── uv.lock
```

## Как это работает (голосовое сообщение)

1. Ты отправляешь голосовое сообщение
2. Бот скачивает `.ogg`, конвертирует в `.wav` (16kHz, моно) через ffmpeg
3. **faster-whisper** распознаёт речь (любой язык)
4. Расшифровка сохраняется в SQLite
5. Текст + история диалога отправляются в OpenRouter с промптом психолога
6. OpenRouter возвращает ответ
7. Бот присылает: **ответ психолога** + **.md файл** для дневника

## Лицензия

MIT
