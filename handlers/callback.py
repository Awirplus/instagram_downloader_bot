from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from core.logger import logger
from services.cache_manager import cache_manager
from services.queue_manager import queue_manager
from utils.users import started_users

@Client.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    # ============================================================
    # دکمه شروع (فعال کردن ربات)
    # ============================================================
    if data == "start_menu":
        started_users.add(user_id)
        logger.info(f"User {user_id} activated the bot via button")
        
        await callback_query.message.edit_text(
            "✅ ربات فعال شد!\n\n"
            "📥 حالا می‌تونی لینک مورد نظرت رو بفرستی:\n"
            "📸 اینستاگرام\n"
            "🎵 ساوندکلاود\n"
            "🎬 یوتیوب\n\n"
            "من برات دانلودش می‌کنم 🚀"
        )
        await callback_query.answer("ربات فعال شد ✅")
        return
    
    # ============================================================
    # دکمه راهنما
    # ============================================================
    elif data == "help":
        await callback_query.message.edit_text(
            "📖 راهنمای استفاده:\n\n"
            "1️⃣ لینک مورد نظرت رو از سرویس مورد نظر کپی کن\n"
            "2️⃣ توی این چت برام بفرست\n"
            "3️⃣ کیفیت مورد نظر رو انتخاب کن\n"
            "4️⃣ منتظر بمون تا دانلود بشه و برات ارسال بشه\n\n"
            "🔹 پشتیبانی:\n"
            "• اینستاگرام (پست، ریلز، استوری)\n"
            "• ساوندکلاود (موسیقی)\n"
            "• یوتیوب (ویدیو)\n\n"
            "🔙 برای بازگشت به منوی اصلی دکمه زیر رو بزن:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_menu")]
            ])
        )
        await callback_query.answer("راهنما")
        return
    
    # ============================================================
    # دکمه برگشت به منوی اصلی
    # ============================================================
    elif data == "back_to_menu":
        user = callback_query.from_user
        first_name = user.first_name or "کاربر عزیز"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 شروع", callback_data="start_menu")],
            [InlineKeyboardButton("📖 راهنما", callback_data="help")]
        ])
        
        await callback_query.message.edit_text(
            f"👋 سلام {first_name}! به ربات دانلودر خوش آمدی!\n\n"
            "📥 می‌تونی لینک اینارو برام بفرستی:\n"
            "📸 اینستاگرام (پست، ریلز، استوری)\n"
            "🎵 ساوندکلاود (موسیقی)\n"
            "🎬 یوتیوب (ویدیو)\n\n"
            "برای شروع روی دکمه کلیک کن 🚀",
            reply_markup=keyboard
        )
        await callback_query.answer("بازگشت به منو")
        return
    
    # ============================================================
    # دکمه‌های بازگشت از دانلود (در صورت خطا یا لغو)
    # ============================================================
    if data == "cancel":
        await callback_query.message.edit_text(
            "❌ عملیات لغو شد.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back_to_menu")]
            ])
        )
        await callback_query.answer("لغو شد ✅")
        return
    
    # ============================================================
    # پردازش دانلود (کیفیت‌ها)
    # ============================================================
    try:
        quality, uid = data.split("|")
        url = cache_manager.get(uid)
        
        if not url:
            await callback_query.message.edit_text(
                "❌ لینک منقضی شده. لطفاً دوباره بفرست.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back_to_menu")]
                ])
            )
            await callback_query.answer("لینک منقضی شده")
            return
        
        # ارسال پیام وضعیت
        quality_text = {
            "best": "بهترین کیفیت",
            "audio": "فقط صدا (MP3)",
            "320": "320 kbps",
            "128": "128 kbps"
        }.get(quality, f"{quality}p")
        
        status_msg = await callback_query.message.edit_text(
            f"⏳ در حال پردازش... (کیفیت: {quality_text})"
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
        await callback_query.message.edit_text(
            f"❌ خطا: {e}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back_to_menu")]
            ])
        )