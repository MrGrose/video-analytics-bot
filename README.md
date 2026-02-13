# Video Analytics Bot
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Aiogram](https://img.shields.io/badge/aiogram-3.13-green.svg)](https://docs.aiogram.dev)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-API-orange.svg)](https://deepseek.com)
[![Poetry](https://img.shields.io/badge/Poetry-✓-blueviolet.svg)](https://python-poetry.org)
[![Docker](https://img.shields.io/badge/Docker-✓-blue.svg)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791.svg)](https://postgresql.org)


Telegram-бот для аналитики видео-статистики через запросы на естественном языке. Бот преобразует русскоязычные вопросы в SQL-запросы и возвращает числовые ответы на основе данных, загруженных из JSON-файла в PostgreSQL.

## О проекте
Этот бот разработан для внутреннего сервиса сбора статистики по видео-креаторам. Данные содержат:

- Итоговую статистику по каждому видео (просмотры, лайки, комментарии, жалобы)
- Почасовые снапшоты для отслеживания динамики изменений

Бот понимает вопросы на русском языке, самостоятельно определяет, из какой таблицы брать данные (итоги или изменения), и возвращает точный числовой ответ.

## Архитектура

Структура проекта
```text
video-analytics-bot/
├── data/                             # JSON-файл с данными
│   └── videos.json                    # Исходные данные (в репозитории)
├── scripts/                          # Вспомогательные скрипты
│   └── load_data.py                   # Загрузка JSON в PostgreSQL
├── src/                              # Исходный код бота
│   ├── bot/                          # Telegram бот (aiogram)
│   │   ├── handlers.py                # Обработчики команд
│   │   └── main.py                    # Точка входа
│   ├── core/                         # Основная логика
│   │   ├── config.py                  # Pydantic настройки
│   │   ├── llm.py                     # DeepSeek API клиент
│   │   ├── logger.py                  # Логирование
│   │   └── prompts.py                  # Промпты для LLM
│   └── db/                            # Работа с БД
│       ├── models.py                   # SQLAlchemy модели
│       ├── repository.py               # Репозиторий для запросов
│       └── session.py                  # Сессии БД
├── docker-compose.yml
├── Dockerfile
├── .gitignore
├── Makefile
├── poetry.lock
├── pyproject.toml
└── README.md
```


### Требования
- Python 3.12 + Poetry
- Aiogram 3.x
- PostgreSQL 17 + asyncpg
- SQLAlchemy 2.0
- DeepSeek API


### Установка и запуск

1. Клонирование
```bash
git clone https://github.com/yourusername/video-analytics-bot.git
cd video-analytics-bot
```

2. Переменные окружения
```bash
.env
# Telegram Bot Token (обязательно)
# BOT_TOKEN=your_telegram_bot_token

# DeepSeek API Key (обязательно)
# DEEPSEEK_API_KEY=your_deepseek_api_key

# PostgreSQL (можно оставить по умолчанию)
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5438 
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgres
# POSTGRES_DB=video_analytics
```

3. Запуск через Docker (рекомендуется)

JSON-файл с тестовыми данными находится в папке data/videos.json.

```bash
# Полный запуск
make up

# Или по шагам:
docker-compose up -d db
docker-compose run --rm bot poetry run python scripts/load_data.py
docker-compose up -d bot
```

4. Локальный запуск (без Docker)
```bash
poetry install
poetry run python scripts/load_data.py
poetry run python -m src.bot.main
```


### Команды бота

- `/start`:	Приветствие
- `/help`:	Инструкция




### Как работает преобразование текста в SQL
Ключевая особенность бота - правильно составленный промпт, который обучает LLM понимать структуру данных и различать типы запросов:

Промпт для LLM (из src/core/prompts.py)
```text
Ты — аналитик данных, эксперт SQL. 
Тебе нужно преобразовать запрос на русском языке в SQL запрос к PostgreSQL.

=== ИНСТРУКЦИЯ ===
1. Проанализируй, что именно нужно посчитать:
   - Количество (COUNT) — "сколько", "количество", "сколько видео"
   - Сумму (SUM) — "сколько просмотров", "суммарный", "общий", "всего"
   - Среднее (AVG) — "среднее", "в среднем"
   - Топ-N (ORDER BY + LIMIT) — "топ-3", "первые 5", "лучшие"

2. Определи таблицу:
   - videos — если вопрос про ИТОГОВУЮ статистику
   - video_snapshots — если вопрос про ИЗМЕНЕНИЯ во времени

=== СХЕМА БАЗЫ ДАННЫХ ===

Таблица videos (итоговая статистика):
- id: UUID — идентификатор видео
- creator_id: VARCHAR — ID автора (всегда в кавычках: '123')
- video_created_at: TIMESTAMPTZ — дата публикации
- views_count: BIGINT — всего просмотров за всё время
- likes_count: BIGINT — всего лайков
- comments_count: BIGINT — всего комментариев
- reports_count: BIGINT — всего жалоб

Таблица video_snapshots (почасовая динамика):
- id: UUID — идентификатор замера
- video_id: UUID — ссылка на видео
- delta_views_count: BIGINT — ПРИРОСТ просмотров за час
- delta_likes_count: BIGINT — ПРИРОСТ лайков за час
- delta_comments_count: BIGINT — ПРИРОСТ комментариев
- delta_reports_count: BIGINT — ПРИРОСТ жалоб
- created_at: TIMESTAMPTZ — время замера

=== ВАЖНЫЕ ПРАВИЛА ===
КЛЮЧЕВОЕ ОТЛИЧИЕ:
- Используй delta_* поля ТОЛЬКО когда спрашивают про ИЗМЕНЕНИЯ:
  * "выросли", "прирост", "получили", "за день", "за час"
- Используй videos.* поля когда спрашивают про ИТОГИ:
  * "всего видео", "общее количество", "в среднем"

Всегда используй COALESCE для SUM: COALESCE(SUM(...), 0)
creator_id всегда в кавычках: WHERE creator_id = '123'
Для дат: DATE(created_at) = '2025-11-28'
```

Логика работы
1. Анализ вопроса: LLM определяет, что нужно посчитать (COUNT, SUM, AVG, TOP-N)
2. Выбор таблицы: Итоги (videos) или изменения (video_snapshots)
3. Сопоставление полей: "просмотры" -> views_count или delta_views_count
4. Обработка дат: "28 ноября 2025" -> DATE(created_at) = '2025-11-28'
5. Генерация SQL: Возвращается только SQL-код без пояснений


### Docker команды
```bash
make up     # Запуск
make down   # Остановка
make logs   # Логи бота
make ps     # Статус контейнеров
make clean  # Полная очистка
```