import aiohttp
from src.core.config import settings
from src.core.logger import get_logger
from src.core.prompts import SQL_GENERATION_PROMPT, SYSTEM_PROMPT

logger = get_logger(__name__)


class DeepSeekClient:
    def __init__(self) -> None:
        self.api_key: str = settings.DEEPSEEK_API_KEY
        self.api_url: str = "https://api.deepseek.com/v1/chat/completions"

        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY is not set!")

    async def generate_sql(self, user_query: str) -> str:
        if not self.api_key:
            raise Exception("DEEPSEEK_API_KEY is not configured")

        prompt: str = SQL_GENERATION_PROMPT.format(user_query=user_query)

        payload: dict = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 300,
            "stream": False,
        }

        headers: dict = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 401:
                        logger.error("Invalid DeepSeek API key")
                        raise Exception("Неверный API ключ DeepSeek")

                    response.raise_for_status()
                    result: dict = await response.json()

                    sql: str = result["choices"][0]["message"]["content"].strip()
                    sql = sql.replace("```sql", "").replace("```", "").strip()

                    if not sql.upper().startswith("SELECT"):
                        raise Exception("Сгенерированный запрос не начинается с SELECT")

                    if ";" in sql and sql.count(";") > 1:
                        raise Exception("Обнаружено несколько SQL запросов")

                    logger.info(f"Generated SQL: {sql}")
                    return sql

        except aiohttp.ClientError as e:
            logger.error(f"DeepSeek API connection error: {e}")
            raise Exception("Ошибка подключения к DeepSeek API")
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            raise Exception(f"Ошибка генерации SQL: {str(e)}")
