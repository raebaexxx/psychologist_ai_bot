# Psychologist AI Bot — План проекта

## Концепция
Telegram бот-психолог/терапевт:
- Принимает голосовые сообщения → расшифровывает → анализирует → отвечает
- Принимает текстовые сообщения → анализирует → отвечает
- Отправляет .md файл с полной расшифровкой для личного дневника

## Технологический стек
| Компонент | Технология |
|---|---|
| Bot Framework | aiogram 3.29+ |
| STT (распознавание речи) | faster-whisper (локально) |
| LLM | OpenRouter (`openrouter/free`) |
| БД | SQLite (через `aiosqlite`) |
| Формат файла | .md / .zip для экспорта |
| Аудио-конвертер | ffmpeg (ogg → wav, 16kHz, моно) |
| Пакетный менеджер | uv |
| Промпт | `bot/prompts/default_therapist.txt` + кастомный через Telegram |

## Архитектура

```
psychologist_ai_bot/
├── bot/
│   ├── main.py              # точка входа, reminder daemon
│   ├── config.py            # настройки из .env
│   ├── handlers/
│   │   ├── commands.py      # /start, /help, /therapists, /select, /prompt,
│   │   │                    # /session, /endsession, /export, /stats, /mood,
│   │   │                    # /remind, /reminds, /setprompt, /resetprompt
│   │   ├── voice.py         # голосовые сообщения
│   │   └── text.py          # текстовые сообщения
│   ├── services/
│   │   ├── transcriber.py   # faster-whisper + ffmpeg + punctuator
│   │   ├── openrouter.py    # OpenRouter API
│   │   ├── diary.py         # генерация .md
│   │   ├── punctuator.py    # rule-based punctuation restoration
│   │   ├── export.py        # экспорт дневника в .zip
│   │   ├── mood.py          # анализ настроения + текстовый график
│   │   └── reminder.py      # фоновая задача напоминаний
│   ├── database/
│   │   ├── db.py            # SQLite (таблицы users, dialogues, reminders, sessions)
│   │   └── models.py        # CRUD для всех таблиц
│   └── prompts/
│       ├── therapist.py     # загрузчик промпта + выбор presets
│       ├── default_therapist.txt
│       └── presets/
│           ├── cbt.txt
│           ├── gestalt.txt
│           ├── jungian.txt
│           └── coach.txt
├── scripts/
│   └── download_model.py    # скачивание модели Whisper
├── .env / .env.example
├── pyproject.toml / uv.lock
└── data/                    # SQLite + custom_prompt.txt (gitignored)
```

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Приветствие |
| `/help` | Список команд |
| `/therapists` | Список терапевтов |
| `/select <name>` | Выбрать подход (cbt, gestalt, jungian, coach) |
| `/prompt` | Показать текущий промпт |
| `/setprompt <text>` | Установить свой промпт |
| `/resetprompt` | Сбросить на дефолтный |
| `/session` | Начать терапевтическую сессию |
| `/endsession` | Завершить сессию + получить summary |
| `/export [days]` | Экспорт дневника в .zip |
| `/stats` | Статистика диалогов |
| `/mood` | График настроения (текстовый) |
| `/remind daily 9:00 текст` | Создать напоминание |
| `/reminds` | Список напоминаний |
| `/remind cancel <id>` | Удалить напоминание |

## Поток работы (голосовое сообщение)
1. Пользователь → голосовое сообщение
2. Бот скачивает `.ogg` файл
3. **ffmpeg** конвертирует `.ogg` → `.wav` (16kHz, моно)
4. **faster-whisper** (vad_filter + beam_size=3) → сырой текст
5. Правила расстановки пунктуации (запятые, точки, вопросы)
6. Сохраняем расшифровку в SQLite + анализируем тональность
7. Отправляем текст + историю в OpenRouter с выбранным промптом
8. OpenRouter → ответ психолога
9. Бот отправляет: анализ + .md файл с расшифровкой
10. Для **текстовых** сообщений — шаги 7-9 (без распознавания)

## Этапы реализации
1. База: структура, config, database, whisper, openrouter, diary
2. Пунктуация: rule-based punctuator
3. Промпты: support presets + custom prompt через Telegram
4. Сессии: /session, /endsession, summary
5. Дневник: /export в .zip
6. Статистика: /stats, /mood (текстовый график)
7. Напоминания: /remind, /reminds, reminder daemon
