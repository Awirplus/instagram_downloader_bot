from pyrogram import Client
import asyncio
import os
import threading
from flask import Flask, jsonify
from core.config import Config
from core.logger import logger
from services.worker import worker
from services.cache_manager import cache_manager

# ============================================================
# اپلیکیشن Flask (برای Render)
# ============================================================
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "Bot is running!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# ============================================================
# اپلیکیشن تلگرام
# ============================================================
telegram_app = Client(
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

async def start_telegram():
    await telegram_app.start()
    logger.info("🤖 Telegram bot started!")
    asyncio.create_task(clean_cache_loop())
    for i in range(Config.NUM_WORKERS):
        asyncio.create_task(worker())
        logger.info(f"✅ Worker {i+1} started")
    await asyncio.Event().wait()

def run_telegram():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_telegram())

# ============================================================
# اجرا
# ============================================================
if __name__ == "__main__":
    threading.Thread(target=run_telegram, daemon=True).start()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
