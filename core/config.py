import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    DOWNLOAD_PATH = "temp"
    MAX_FILE_SIZE = 2 * 1024 ** 3  # 2GB
    CACHE_TTL = 3600  # 1 ساعت
    NUM_WORKERS = 5
    
    COOKIE_FILE = "cookies.txt"