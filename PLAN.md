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
| STT (распознавание речи) | faster-whisper (модель `medium`, локально, бесплатно) |
| LLM | OpenRouter (`openrouter/free` — роутер по 27+ бесплатным моделям) |
| БД | SQLite (через `aiosqlite`) |
| Формат файла | .md с полной расшифровкой |
| Аудио-конвертер | ffmpeg (ogg → wav, 16kHz, моно) |

## Архитектура

```
psychologist_ai_bot/
├── bot/
│   ├── __init__.py
│   ├── main.py              # точка входа, запуск полинга
│   ├── config.py            # токены, настройки (pydantic-settings)
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── voice.py         # обработка голосовых сообщений
│   │   ├── text.py          # обработка текстовых сообщений
│   │   └── commands.py      # /start, /help
│   ├── services/
│   │   ├── __init__.py
│   │   ├── transcriber.py   # faster-whisper: ogg→wav→текст
│   │   ├── openrouter.py    # HTTP клиент к OpenRouter API
│   │   └── diary.py         # генерация .md файла
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py            # инициализация SQLite
│   │   └── models.py        # create table, crud
│   └── prompts/
│       ├── __init__.py
│       └── therapist.py     # системный промпт психолога
├── .env                     # BOT_TOKEN, OPENROUTER_API_KEY
├── .gitignore
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Поток работы (голосовое сообщение)
1. Пользователь → голосовое сообщение
2. Бот скачивает `.ogg` файл
3. **ffmpeg** конвертирует `.ogg` → `.wav` (16kHz, моно)
4. **faster-whisper** (medium) → сырой текст
5. Сохраняем расшифровку в SQLite
6. Отправляем текст + историю в OpenRouter с системным промптом
7. OpenRouter → ответ психолога
8. Бот отправляет: анализ + .md файл с расшифровкой
9. Для **текстовых** сообщений — шаги 6-8 (без распознавания)

## Системный промпт
Роль: профессиональный психолог-терапевт с эмпатией, без осуждения, задающий уточняющие вопросы, использующий техники активного слушания. Запрет на медицинские диагнозы. Ответ на языке пользователя.

## Этапы реализации
1. Сохранение плана, Git init + GitHub
2. Структура, requirements.txt, .env
3. config.py
4. database/
5. prompts/therapist.py
6. services/transcriber.py
7. services/openrouter.py
8. services/diary.py
9. handlers/ (voice, text, commands)
10. main.py
11. Dockerfile + docker-compose.yml
12. Проверка сборки
