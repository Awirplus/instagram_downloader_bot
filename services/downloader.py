import yt_dlp
import os
import time
from core.logger import logger
from core.config import Config

class InstagramDownloader:
    
    def __init__(self):
        self.cookie_file = Config.COOKIE_FILE
    
    def download(self, url: str, quality: str = "best"):
        """
        دانلود از اینستاگرام
        کیفیت: best, 720, 360
        """
        
        # انتخاب فرمت
        fmt = "best"
        if quality == "720":
            fmt = "best[height<=720]"
        elif quality == "360":
            fmt = "best[height<=360]"
        
        opts = {
            "format": fmt,
            "quiet": True,
            "noplaylist": True,
            "outtmpl": f"{Config.DOWNLOAD_PATH}/%(id)s.%(ext)s",
            "cookiefile": self.cookie_file,
            "retries": 3,
            "fragment_retries": 3,
            "socket_timeout": 15,
            "ignoreerrors": True,
            "continuedl": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "progress_hooks": [self._progress_hook]
        }
        
        # تلاش مجدد
        for attempt in range(3):
            try:
                logger.info(f"Download attempt {attempt+1} for {url}")
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    if not info:
                        raise Exception("Empty info returned")
                    
                    file_path = ydl.prepare_filename(info)
                    
                    if os.path.exists(file_path):
                        # بررسی حجم
                        size = os.path.getsize(file_path)
                        if size > Config.MAX_FILE_SIZE:
                            os.remove(file_path)
                            raise Exception(f"File too large: {size/1024**3:.2f}GB")
                        
                        # تشخیص نوع فایل
                        ext = os.path.splitext(file_path)[1].lower()
                        if ext in ['.mp4', '.mov', '.avi']:
                            file_type = 'video'
                        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                            file_type = 'photo'
                        else:
                            file_type = 'unknown'
                        
                        return {
                            'path': file_path,
                            'type': file_type,
                            'ext': ext
                        }
                    
            except Exception as e:
                logger.error(f"Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        
        raise Exception("Download failed after 3 attempts")
    
    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', 'N/A')
            logger.info(f"⬇️ {percent} at {speed}")