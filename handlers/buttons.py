from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class DownloadButtons:
    
    @staticmethod
    def quality_buttons(uid: str):
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔥 بهترین کیفیت", callback_data=f"best|{uid}")
            ],
            [
                InlineKeyboardButton("⚡ 720p", callback_data=f"720|{uid}"),
                InlineKeyboardButton("⚡ 360p", callback_data=f"360|{uid}")
            ],
            [
                InlineKeyboardButton("❌ لغو", callback_data="cancel")
            ]
        ])
    
    @staticmethod
    def cancel_button():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ لغو عملیات", callback_data="cancel")]
        ])