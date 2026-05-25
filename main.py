import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from config import settings
from handlers import start, image

logger = logging.getLogger(__name__)

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
    logger.info(f"Render uchun veb-server {port}-portda ishga tushdi.")

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Bot va Dispatcher-ni yaratish
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    # Handlerlarni ulash
    dp.include_router(start.router)
    dp.include_router(image.router)
    
    # Veb-serverni orqa fonda parallel ishga tushirish
    asyncio.create_task(start_web_server())
    
    logger.info("Bot polling rejimida ishga tushmoqda...")
    await dp.start_polling(bot)

if name == "__main__":
    asyncio.run(main())
