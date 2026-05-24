import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from config.settings import BOT_TOKEN
from handlers import start, image

# Render uchun kichik sun'iy veb-server (Xatolik bermasligi uchun)
from datetime import datetime
async def dummy_server():
    async def handle_client(reader, writer):
        request = await reader.read(1024)
        response = b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK"
        writer.write(response)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    port = int(os.environ.get("PORT", 10000))
    server = await asyncio.start_server(handle_client, "0.0.0.0", port)
    logging.info(f"Dummy server running on port {port}")
    async with server:
        await server.serve_forever()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if not BOT_TOKEN:
        logging.error("BOT_TOKEN topilmadi! .env yoki Environment Variables'ni tekshiring.")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Routerlarni ulash
    dp.include_router(start.router)
    dp.include_router(image.router)

    logging.info("Bot ishga tushmoqda...")
    
    # Bot va dummy serverni parallel ishga tushiramiz
    await asyncio.gather(
        dp.start_polling(bot),
        dummy_server()
    )

if name == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi.")
