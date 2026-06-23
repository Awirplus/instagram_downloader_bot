from pyrogram import Client
import asyncio
import os
from core.config import Config
from core.logger import logger
from services.worker import worker
from services.cache_manager import cache_manager
from flask import Flask, jsonify
import threading

# ============================================================
# ایجاد اپلیکیشن Flask برای Render (اشغال پورت)
# ============================================================
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "Bot is running!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

def run_flask():
    """اجرای سرور Flask برای اشغال پورت"""
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# ============================================================
# ایجاد اپلیکیشن تلگرام
# ============================================================
telegram_app = Client(
    "insta_downloader_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="handlers")
)

async def clean_cache_loop():
    """پاکسازی خودکار کش"""
    while True:
        await asyncio.sleep(300)
        removed = cache_manager.clean()
        if removed > 0:
            logger.info(f"🧹 {removed} expired cache items removed")

async def start_bot():
    await telegram_app.start()
    logger.info("🤖 Bot is running!")
    
    asyncio.create_task(clean_cache_loop())
    
    for i in range(Config.NUM_WORKERS):
        asyncio.create_task(worker())
        logger.info(f"✅ Worker {i+1} started")
    
    await asyncio.Event().wait()

# ============================================================
# اجرا
# ============================================================
if __name__ == "__main__":
    # اجرای Flask در یک ترد جداگانه
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # اجرای ربات تلگرام
    telegram_app.run(start_bot())
