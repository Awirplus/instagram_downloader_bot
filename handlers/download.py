from pyrogram import Client, filters
import uuid
from core.logger import logger
from services.cache_manager import cache_manager
from services.queue_manager import queue_manager
from handlers.buttons import DownloadButtons

@Client.on_message(filters.private & filters.text & ~filters.command("start"))
async def handle_link(client, message):
    url = message.text.strip()
    
    # اعتبارسنجی لینک
    if "instagram.com" not in url:
        await message.reply_text("❌ لطفاً یک لینک معتبر از اینستاگرام بفرست.")
        return
    
    # ذخیره در کش
    uid = str(uuid.uuid4())[:8]
    cache_manager.add(uid, url)
    
    logger.info(f"New download request: {url} from user {message.from_user.id}")
    
    # نمایش دکمه‌های کیفیت
    await message.reply_text(
        "🎬 لینک دریافت شد! کیفیت مورد نظر رو انتخاب کن:",
        reply_markup=DownloadButtons.quality_buttons(uid)
    )