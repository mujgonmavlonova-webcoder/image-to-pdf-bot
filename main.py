import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from config.settings import BOT_TOKEN
from handlers import start, image

# Render "Sog'lomlik testi" (Health Check) uchun aiohttp veb-serveri
async def handle_root(request):
    return web.Response(text="Bot is running smoothly!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_root)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Render uchun veb-server {port}-portda ishga tushdi.")

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if not BOT_TOKEN:
        logging.error("BOT_TOKEN topilmadi! Environment Variables'ni tekshiring.")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Routerlarni ro'yxatdan o'tkazish
    dp.include_router(start.router)
    dp.include_router(image.router)

    # Bir vaqtning o'zida ham veb-serverni, ham botni ishga tushiramiz
    await start_web_server()
    
    logging.info("Telegram Bot Long Polling rejimida ishga tushmoqda...")
    await dp.start_polling(bot)

if name == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi.")
