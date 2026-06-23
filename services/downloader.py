import yt_dlp
import os
import time
import re
import requests
from core.logger import logger
from core.config import Config

# ============================================================
# تابع تشخیص سرویس
# ============================================================
def detect_service(url):
    if "instagram.com" in url:
        return "instagram"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "soundcloud.com" in url or "on.soundcloud.com" in url:
        return "soundcloud"
    else:
        return None

class InstagramDownloader:
    
    def __init__(self):
        self.cookie_file = Config.COOKIE_FILE
    
    def download(self, url: str, quality: str = "best"):
        service = detect_service(url)
        
        # دنبال کردن لینک‌های کوتاه ساوندکلاود
        if service == "soundcloud" and "on.soundcloud.com" in url:
            try:
                response = requests.head(url, allow_redirects=True, timeout=10)
                url = response.url
                logger.info(f"Redirected to: {url}")
            except Exception as e:
                logger.warning(f"Could not follow redirect: {e}")
        
        # ============================================================
        # تنظیمات پایه
        # ============================================================
        opts = {
            "quiet": True,
            "noplaylist": True,
            "outtmpl": f"{Config.DOWNLOAD_PATH}/%(id)s.%(ext)s",
            "format": "best",
            "retries": 10,
            "fragment_retries": 10,
            "socket_timeout": 30,
            "ignoreerrors": True,
            "continuedl": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "progress_hooks": [self._progress_hook],
            "ffmpeg_location": r"D:\ffmpeg\bin\ffmpeg.exe"
        }
        
        # ============================================================
        # تنظیمات مخصوص ساوندکلاود با کیفیت‌های مختلف
        # ============================================================
        if service == "soundcloud":
            if quality == "320":
                opts["format"] = "bestaudio[abr<=320]/bestaudio/best"
            elif quality == "128":
                opts["format"] = "bestaudio[abr<=128]/bestaudio/best"
            else:  # best
                opts["format"] = "bestaudio/best"
            
            opts["extractaudio"] = True
            opts["audioformat"] = "mp3"
            opts["outtmpl"] = f"{Config.DOWNLOAD_PATH}/%(title)s.%(ext)s"
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {
                    "key": "EmbedThumbnail",
                },
                {
                    "key": "FFmpegMetadata",
                }
            ]
            opts["writethumbnail"] = True
            opts["embedthumbnail"] = True
            opts["extract_flat"] = False
            opts["force_generic_extractor"] = False
        
        # ============================================================
        # تنظیمات مخصوص اینستاگرام
        # ============================================================
        elif service == "instagram":
            opts["cookiefile"] = self.cookie_file
            opts["format"] = "best"
            opts["writethumbnail"] = True
            opts["extract_flat"] = False
            opts["http_headers"] = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            }
        
        # ============================================================
        # تنظیمات مخصوص یوتیوب با کیفیت‌های مختلف و تامبنیل
        # ============================================================
        elif service == "youtube":
            if quality == "1080":
                fmt = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]"
            elif quality == "720":
                fmt = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]"
            elif quality == "480":
                fmt = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]"
            elif quality == "360":
                fmt = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]"
            elif quality == "audio":
                fmt = "bestaudio/best"
                opts["extractaudio"] = True
                opts["audioformat"] = "mp3"
                opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            else:  # best
                fmt = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]"
            
            opts["format"] = fmt
            opts["outtmpl"] = f"{Config.DOWNLOAD_PATH}/%(title)s.%(ext)s"
            opts["writethumbnail"] = True
            opts["http_headers"] = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            }
        
        # ============================================================
        # تلاش برای دانلود (3 بار)
        # ============================================================
        for attempt in range(3):
            try:
                logger.info(f"Download attempt {attempt+1} for {url}")
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    if not info:
                        raise Exception("Empty info returned")
                    
                    file_path = ydl.prepare_filename(info)
                    
                    if not os.path.exists(file_path):
                        for f in os.listdir(Config.DOWNLOAD_PATH):
                            if f.endswith(('.mp3', '.m4a', '.mp4', '.mkv', '.webm')):
                                file_path = os.path.join(Config.DOWNLOAD_PATH, f)
                                break
                    
                    if os.path.exists(file_path):
                        # =============================================
                        # پیدا کردن تامبنیل (برای اینستاگرام و یوتیوب)
                        # =============================================
                        thumbnail_path = None
                        if service in ["instagram", "youtube"]:
                            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                                temp_thumb = os.path.splitext(file_path)[0] + ext
                                if os.path.exists(temp_thumb):
                                    thumbnail_path = temp_thumb
                                    logger.info(f"Thumbnail found: {thumbnail_path}")
                                    break
                        
                        # =============================================
                        # حذف فایل‌های کاور اضافی (فقط برای ساوندکلاود)
                        # =============================================
                        if service == "soundcloud":
                            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                                cover_path = os.path.splitext(file_path)[0] + ext
                                if os.path.exists(cover_path):
                                    try:
                                        os.remove(cover_path)
                                        logger.info(f"Cover file removed: {cover_path}")
                                    except:
                                        pass
                        
                        # تشخیص نوع فایل
                        ext = os.path.splitext(file_path)[1].lower()
                        if ext in ['.mp3', '.m4a', '.aac', '.wav']:
                            file_type = 'audio'
                        elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
                            file_type = 'video'
                        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                            file_type = 'photo'
                        else:
                            file_type = 'unknown'
                        
                        return {
                            'path': file_path,
                            'type': file_type,
                            'ext': ext,
                            'thumbnail': thumbnail_path
                        }
                    
            except Exception as e:
                logger.error(f"Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        
        raise Exception("Download failed after 3 attempts")
    
    def _progress_hook(self, d):
        try:
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '0%')
                speed = d.get('_speed_str', 'N/A')
                percent = re.sub(r'\x1b\[[0-9;]*m', '', percent)
                speed = re.sub(r'\x1b\[[0-9;]*m', '', speed)
                logger.info(f"⬇️ {percent} at {speed}")
        except:
            pass