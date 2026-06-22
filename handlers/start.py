from pyrogram import Client, filters
from core.logger import logger

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    user = message.from_user
    logger.info(f"User {user.id} (@{user.username}) started the bot")
    
    await message.reply_text(
        "👋 سلام! به ربات دانلودر اینستاگرام خوش آمدی!\n\n"
        "📥 کافیه لینک پست، ریلز یا استوری اینستاگرام رو برام بفرستی.\n"
        "من برات دانلودش می‌کنم و کیفیت رو هم می‌تونی انتخاب کنی.\n\n"
        "🔹 مثال:\n"
        "`https://www.instagram.com/reel/ABC123/`\n\n"
        "🚀 منتظر لینکت هستم..."
    )