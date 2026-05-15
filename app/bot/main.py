"""aiogram polling entrypoint."""

import asyncio

from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.core.config import get_settings
from app.core.logging import configure_logging


async def main() -> None:
    """Run Telegram bot polling."""
    configure_logging()
    settings = get_settings()
    bot = Bot(settings.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
