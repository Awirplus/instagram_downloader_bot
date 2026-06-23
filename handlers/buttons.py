from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class DownloadButtons:
    
    @staticmethod
    def quality_buttons(uid: str):
        """دکمه‌های پیش‌فرض (برای مواقع خطا)"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔥 بهترین کیفیت", callback_data=f"best|{uid}"),
            ],
            [
                InlineKeyboardButton("❌ لغو", callback_data="cancel")
            ]
        ])
    
    @staticmethod
    def youtube_quality_buttons(uid: str, heights: list):
        """دکمه‌های پویا برای یوتیوب بر اساس کیفیت‌های موجود (فقط 360 به بالا)"""
        buttons = []
        
        # فیلتر کردن کیفیت‌های زیر 360
        heights = [h for h in heights if h >= 360]
        
        # اضافه کردن دکمه‌ها از کم به زیاد
        for h in heights:
            quality_text = f"{h}p"
            if h >= 1080:
                quality_text = "🔥 1080p"
            elif h >= 720:
                quality_text = f"⚡ {h}p"
            else:
                quality_text = f"📱 {h}p"
            
            buttons.append([InlineKeyboardButton(quality_text, callback_data=f"{h}|{uid}")])
        
        # اضافه کردن دکمه دانلود صدا
        buttons.append([InlineKeyboardButton("🎵 فقط صدا (MP3)", callback_data=f"audio|{uid}")])
        buttons.append([InlineKeyboardButton("❌ لغو", callback_data="cancel")])
        buttons.append([InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back_to_menu")])  # ← اضافه شد
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def soundcloud_quality_buttons(uid: str):
        """دکمه‌های کیفیت صوتی برای ساوندکلاود"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 320 kbps (بهترین)", callback_data=f"320|{uid}"),
            ],
            [
                InlineKeyboardButton("🎵 128 kbps (معمولی)", callback_data=f"128|{uid}"),
            ],
            [
                InlineKeyboardButton("❌ لغو", callback_data="cancel")
            ],
            [
                InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back_to_menu")  # ← اضافه شد
            ]
        ])
    
    @staticmethod
    def instagram_buttons(uid: str):
        """دکمه‌های اینستاگرام (فقط بهترین کیفیت)"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📸 دانلود با بهترین کیفیت", callback_data=f"best|{uid}"),
            ],
            [
                InlineKeyboardButton("❌ لغو", callback_data="cancel")
            ],
            [
                InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back_to_menu")  # ← اضافه شد
            ]
        ])
    
    @staticmethod
    def cancel_button():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ لغو عملیات", callback_data="cancel")]
        ])
    
    @staticmethod
    def home_button():
        """دکمه بازگشت به منوی اصلی"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back_to_menu")]
        ])