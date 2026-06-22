from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from core.logger import logger
from services.cache_manager import cache_manager
from services.queue_manager import queue_manager

@Client.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    data = callback_query.data
    
    # لغو عملیات
    if data == "cancel":
        await callback_query.message.edit_text("❌ عملیات لغو شد.")
        await callback_query.answer("لغو شد ✅")
        return
    
    # پردازش دانلود
    try:
        quality, uid = data.split("|")
        url = cache_manager.get(uid)
        
        if not url:
            await callback_query.message.edit_text("❌ لینک منقضی شده. لطفاً دوباره بفرست.")
            await callback_query.answer("لینک منقضی شده")
            return
        
        # ارسال پیام وضعیت
        status_msg = await callback_query.message.edit_text(
            f"⏳ در حال پردازش... (کیفیت: {quality})"
        )
        
        # اضافه به صف
        await queue_manager.add({
            'client': client,
            'message': callback_query.message,
            'status_msg': status_msg,
            'url': url,
            'quality': quality,
            'user_id': callback_query.from_user.id
        })
        
        await callback_query.answer("✅ در صف قرار گرفت")
        
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await callback_query.message.edit_text(f"❌ خطا: {e}")