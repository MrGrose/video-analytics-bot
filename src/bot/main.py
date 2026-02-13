import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers import router
from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info(settings.SYS_STARTUP)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
