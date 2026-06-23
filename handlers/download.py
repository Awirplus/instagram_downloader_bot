from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
from core.logger import logger
from services.cache_manager import cache_manager
from services.queue_manager import queue_manager
from handlers.buttons import DownloadButtons
from services.downloader import detect_service
from utils.users import started_users
import yt_dlp

@Client.on_message(filters.private & filters.text & ~filters.command("start"))
async def handle_link(client, message):
    user_id = message.from_user.id
    
    # ============================================================
    # چک کردن اینکه کاربر ربات رو استارت کرده یا نه
    # ============================================================
    if user_id not in started_users:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 استارت ربات", callback_data="start_menu")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back_to_menu")]
        ])
        await message.reply_text(
            "❌ لطفاً ابتدا ربات رو با دستور /start یا دکمه زیر فعال کن!",
            reply_markup=keyboard
        )
        return
    
    # ادامه کد قبلی...
    url = message.text.strip()
    
    # تشخیص سرویس
    service = detect_service(url)
    if not service:
        await message.reply_text(
            "❌ لطفاً یک لینک معتبر از اینستاگرام، ساوندکلاود یا یوتیوب بفرست.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back_to_menu")]
            ])
        )
        return
    
    # ذخیره در کش
    uid = str(uuid.uuid4())[:8]
    cache_manager.add(uid, url)
    
    logger.info(f"New download request: {url} from user {message.from_user.id}")
    
    # ============================================================
    # برای یوتیوب: دریافت کیفیت‌های موجود (فقط 360 به بالا)
    # ============================================================
    if service == "youtube":
        try:
            ydl_opts = {"quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                heights = set()
                for f in formats:
                    height = f.get('height')
                    if height and 360 <= height <= 1080:
                        heights.add(height)
                
                heights = sorted(heights)
                
                if not heights:
                    heights = [360, 480, 720, 1080]
                
                await message.reply_text(
                    "🎬 لینک یوتیوب دریافت شد! کیفیت مورد نظر رو انتخاب کن:",
                    reply_markup=DownloadButtons.youtube_quality_buttons(uid, heights)
                )
                return
                
        except Exception as e:
            logger.error(f"Error getting YouTube formats: {e}")
            await message.reply_text(
                "🎬 لینک دریافت شد! برای دانلود کلیک کن:",
                reply_markup=DownloadButtons.quality_buttons(uid)
            )
            return
    
    # ============================================================
    # برای ساوندکلاود: دکمه‌های کیفیت صوتی
    # ============================================================
    elif service == "soundcloud":
        await message.reply_text(
            "🎵 لینک ساوندکلاود دریافت شد! کیفیت صوتی رو انتخاب کن:",
            reply_markup=DownloadButtons.soundcloud_quality_buttons(uid)
        )
        return
    
    # ============================================================
    # برای اینستاگرام: فقط بهترین کیفیت
    # ============================================================
    elif service == "instagram":
        await message.reply_text(
            "📸 لینک اینستاگرام دریافت شد! برای دانلود کلیک کن:",
            reply_markup=DownloadButtons.instagram_buttons(uid)
        )
        return