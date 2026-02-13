from collections import deque
from typing import Any

from aiogram import Router, types
from aiogram.filters import Command

from src.core.config import settings
from src.core.llm import DeepSeekClient
from src.core.logger import get_logger
from src.db.repository import AnalyticsRepository
from src.db.session import get_db

router = Router()
logger = get_logger(__name__)

llm_client = DeepSeekClient()
last_queries: dict[int, deque[dict[str, Any]]] = {}

if not settings.DEEPSEEK_API_KEY:
    logger.error(settings.MSG_NO_API_KEY)


@router.message(Command("start"))
async def start_command(message: types.Message) -> None:
    await message.reply(settings.MSG_START)


@router.message(Command("help"))
async def help_command(message: types.Message) -> None:
    await message.reply(settings.MSG_HELP)


@router.message()
async def analytics_query(message: types.Message) -> None:
    if not message.text:
        await message.reply(settings.MSG_SHORT_QUERY)
        return

    user_query: str = message.text.strip()
    user_id: int = message.from_user.id if message.from_user else 0

    if len(user_query) < 5:
        await message.reply(settings.MSG_SHORT_QUERY)
        return

    if message.bot:
        await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        sql_query: str = await llm_client.generate_sql(user_query)
        logger.info(f"SQL for '{user_query}': {sql_query}")

        result: Any = None
        async for session in get_db():
            repo = AnalyticsRepository(session)
            result = await repo.execute_sql_query(sql_query)
            break

        if user_id and result is not None:
            if user_id not in last_queries:
                last_queries[user_id] = deque(maxlen=10)
            last_queries[user_id].append(
                {"query": user_query, "sql": sql_query, "result": result}
            )

        response: str
        if isinstance(result, int):
            response = f"{result:,}"
        elif result is not None:
            response = f"\n{result}"
        else:
            response = "Нет данных"

        await message.reply(response, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error: {user_query} - {e}")
        await message.reply(settings.MSG_ERROR)


@router.message(Command("history"))
async def show_history(message: types.Message) -> None:
    user_id: int = message.from_user.id if message.from_user else 0

    if not user_id or user_id not in last_queries or not last_queries[user_id]:
        await message.reply("История пуста")
        return

    history_text: str = "Последние запросы:\n\n"
    for i, item in enumerate(last_queries[user_id], 1):
        result_str: str = str(item.get("result", "?"))
        history_text += f"{i}. {item.get('query', '?')} → {result_str}\n"

    await message.reply(history_text)
