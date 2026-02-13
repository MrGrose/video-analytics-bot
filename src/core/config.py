from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "video_analytics"

    BOT_TOKEN: str = ""
    DEEPSEEK_API_KEY: str = ""

    MSG_START: str = """
        Привет! Я бот для аналитики видео.

        Я преобразую твои вопросы на русском языке в SQL запросы и отвечаю числом.

        Примеры:
        • Сколько всего видео в системе?
        • Топ-5 видео по просмотрам
        • На сколько просмотров выросли все видео 28 ноября 2025?
        • Какой автор имеет больше всего видео?

        Команды:
        /start - Показать это сообщение
        /help - Помощь
    """

    MSG_HELP: str = """
        Как пользоваться:

        1. Задай вопрос на русском языке
        2. Бот возвращает число

        Формулируй вопросы конкретно:
        • "Сколько видео у креатора 123?"
        • "Сумма лайков за ноябрь 2025"
        • "Топ-3 видео по комментариям"
        • "Средний прирост просмотров за 26 ноября"

        Не понимает вопрос - переформулируй.
    """

    MSG_SHORT_QUERY: str = "Слишком короткий запрос. Напишите подробнее."
    MSG_ERROR: str = "Ошибка. Переформулируйте вопрос."
    MSG_NO_API_KEY: str = "DeepSeek API ключ не настроен!"
    MSG_TYPING: str = "печатает..."

    SYS_STARTUP: str = "Bot started"
    SYS_SHUTDOWN: str = "Bot stopped"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
