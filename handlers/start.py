from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.logger import logger
from utils.users import started_users

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    user = message.from_user
    first_name = user.first_name or "کاربر عزیز"
    user_id = user.id
    
    # اضافه کردن کاربر به لیست استارت‌شده‌ها
    started_users.add(user_id)
    logger.info(f"User {user_id} (@{user.username}) started the bot")
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 شروع", callback_data="start_menu")],
        [InlineKeyboardButton("📖 راهنما", callback_data="help")]
    ])
    
    await message.reply_text(
        f"👋 سلام {first_name}! به ربات دانلودر خوش آمدی!\n\n"
        "📥 می‌تونی لینک اینارو برام بفرستی:\n"
        "📸 اینستاگرام (پست، ریلز، استوری)\n"
        "🎵 ساوندکلاود (موسیقی)\n"
        "🎬 یوتیوب (ویدیو)\n\n"
        "برای شروع روی دکمه کلیک کن 🚀",
        reply_markup=keyboard
    )