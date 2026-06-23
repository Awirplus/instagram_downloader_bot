from pyrogram import Client
import asyncio
import os
from core.config import Config
from core.logger import logger
from services.worker import worker
from services.cache_manager import cache_manager

# اطمینان از وجود پوشه‌ها
os.makedirs("temp", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ایجاد اپلیکیشن
app = Client(
    "insta_downloader_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="handlers")
)

async def clean_cache_loop():
    while True:
        await asyncio.sleep(300)
        removed = cache_manager.clean()
        if removed > 0:
            logger.info(f"🧹 {removed} expired cache items removed")

async def start_bot():
    await app.start()
    logger.info("🤖 Bot is running!")
    
    asyncio.create_task(clean_cache_loop())
    
    for i in range(Config.NUM_WORKERS):
        asyncio.create_task(worker())
        logger.info(f"✅ Worker {i+1} started")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    app.run(start_bot())
