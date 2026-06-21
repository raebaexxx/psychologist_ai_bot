# Psychologist AI Bot

Telegram-бот — личный психолог-терапевт. Принимает голосовые и текстовые сообщения, расшифровывает, анализирует через AI и даёт эмпатичный ответ психолога. Поддерживает несколько терапевтических подходов, сессии, дневник с экспортом, анализ настроения и ежедневные напоминания.

## Возможности

- **🎤 Голосовые сообщения** — расшифровка через faster-whisper (бесплатно, локально), анализ через OpenRouter, ответ психолога + `.md` файл с расшифровкой
- **💬 Текстовые сообщения** — анализ и ответ психолога
- **🧠 Контекст** — бот помнит историю диалога (хранится в SQLite)
- **🔄 Терапевтические подходы** — 4 встроенных пресета (КПТ, гештальт, юнгианский, коуч) + свой промпт через Telegram
- **📅 Сессии** — режим сессии с summary по завершении
- **📔 Дневник** — к каждому сообщению приходит `.md` файл; экспорт всех записей в `.zip`
- **📊 Настроение** — текстовый график тональности за 7 дней
- **⏰ Напоминания** — ежедневные напоминания с фоновым daemon
- **🔒 Конфиденциально** — всё хранится локально, твои данные не уходят третьим лицам (кроме OpenRouter)

## Команды

| Команда | Описание |
|---|---|
| `/start` | Приветствие + текущий терапевт |
| `/help` | Список команд |
| `/therapists` | Список доступных подходов |
| `/select cbt` | Выбрать подход (cbt, gestalt, jungian, coach) |
| `/prompt` | Показать текущий промпт |
| `/setprompt <text>` | Установить свой промпт |
| `/resetprompt` | Сбросить на дефолтный |
| `/session` | Начать сессию |
| `/endsession` | Завершить сессию + summary |
| `/export [дней]` | Скачать дневник (.zip) |
| `/stats` | Статистика диалогов |
| `/mood` | График настроения |
| `/remind daily 9:00 текст` | Создать напоминание |
| `/reminds` | Мои напоминания |
| `/remind cancel <id>` | Удалить напоминание |

Также можно отправить `.txt` файл — он станет твоим системным промптом.

## Технологии

| Компонент | |
|---|---|
| Bot Framework | aiogram 3.29 |
| Распознавание речи | faster-whisper (локально) |
| AI | OpenRouter (бесплатные модели, `openrouter/free`) |
| База данных | SQLite (aiosqlite) |
| Пакетный менеджер | uv |
| Аудио-конвертер | ffmpeg |

## Системные требования (Whisper)

| Модель | RAM | CPU | Качество |
|---|---|---|---|
| `tiny` | ~300 MB | 1 ядро | Базовое |
| `base` | ~500 MB | 1 ядро | Среднее |
| **`small`** | **~1 GB** | **1 ядро** | **Хорошее (для 2GB VPS)** |
| `medium` | ~2.5 GB | 2+ ядра | Отличное |
| `large-v3` | ~6 GB | 4+ ядра | Максимальное |

Выбирается параметром `WHISPER_MODEL_SIZE` в `.env`.

## Установка и запуск

### 1. Клонировать

```bash
git clone https://github.com/raebaexxx/psychologist_ai_bot.git
cd psychologist_ai_bot
```

### 2. Настроить `.env`

```bash
cp .env.example .env
nano .env
```

Параметры:

- **BOT_TOKEN** — токен от [@BotFather](https://t.me/BotFather)
- **OPENROUTER_API_KEY** — ключ от [OpenRouter](https://openrouter.ai/) (бесплатно, без карты)
- **WHISPER_MODEL_SIZE** — размер модели (small для 2GB VPS)
- **HF_TOKEN** — токен huggingface (ускоряет скачивание, опционально)

### 3. Установить зависимости

```bash
uv sync
```

### 4. Убедиться, что ffmpeg установлен

```bash
sudo apt install ffmpeg      # Debian/Ubuntu
brew install ffmpeg          # macOS
sudo pacman -S ffmpeg        # Arch
```

### 5. Скачать модель Whisper

```bash
uv run python scripts/download_model.py small
```

Модель сохраняется в `~/.cache/huggingface/hub/`. Если есть системный прокси (`all_proxy`), скрипт сам его уберёт на время скачивания.

### 6. Запустить

```bash
uv run python -m bot.main
```

## Запуск на сервере (tmux)

```bash
tmux new-session -s psychologist
cd ~/psychologist_ai_bot
uv run python -m bot.main
```

`Ctrl+B`, затем `D` — отключиться. Бот останется в фоне.

### Автозапуск (crontab)

```bash
crontab -e
```

```
@reboot cd /root/psychologist_ai_bot && tmux new-session -d -s psychologist 'uv run python -m bot.main'
```

## Структура проекта

```
psychologist_ai_bot/
├── bot/
│   ├── main.py                 # точка входа
│   ├── config.py               # настройки из .env
│   ├── handlers/
│   │   ├── commands.py         # все команды
│   │   ├── voice.py            # голосовые сообщения
│   │   └── text.py             # текстовые сообщения
│   ├── services/
│   │   ├── transcriber.py      # faster-whisper + ffmpeg
│   │   ├── punctuator.py       # расстановка пунктуации
│   │   ├── openrouter.py       # OpenRouter API
│   │   ├── diary.py            # генератор .md
│   │   ├── export.py           # экспорт дневника
│   │   ├── mood.py             # анализ настроения
│   │   └── reminder.py         # напоминания (daemon)
│   ├── database/
│   │   ├── db.py               # SQLite
│   │   └── models.py           # CRUD
│   └── prompts/
│       ├── therapist.py        # загрузчик промпта
│       ├── default_therapist.txt
│       └── presets/
│           ├── cbt.txt
│           ├── gestalt.txt
│           ├── jungian.txt
│           └── coach.txt
└── scripts/
    └── download_model.py
```

## Поток работы (голосовое сообщение)

1. Ты отправляешь голосовое сообщение
2. Бот скачивает `.ogg`, конвертирует в `.wav` (16kHz, моно) через ffmpeg
3. **faster-whisper** распознаёт речь
4. Правила расставляют пунктуацию
5. Расшифровка + тональность сохраняются в SQLite
6. Текст + история + выбранный промпт отправляются в OpenRouter
7. OpenRouter возвращает ответ
8. Бот присылает: **ответ психолога** + **.md файл** для дневника

## Лицензия

MIT
