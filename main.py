"""
main.py
~~~~~~~
Bot ishga tushurish nuqtasi.

Lokal ishlatish:
    python main.py
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from handlers import image_router, start_router


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Image → PDF Bot ishga tushmoqda…")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # FSM uchun MemoryStorage (Render free tier uchun yetarli)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Routerlarni ro'yxatdan o'tkazish
    dp.include_router(start_router)
    dp.include_router(image_router)

    # Bot o'chiq paytida kelgan update'larni o'tkazib yuborish
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Bot ishlamoqda. To'xtatish uchun Ctrl+C bosing.")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    asyncio.run(main())
