import time
from core.config import Config

class CacheManager:
    def __init__(self):
        self.cache = {}
    
    def add(self, key: str, value: str):
        self.cache[key] = {
            'url': value,
            'time': time.time()
        }
    
    def get(self, key: str):
        item = self.cache.get(key)
        if not item:
            return None
        
        if time.time() - item['time'] > Config.CACHE_TTL:
            del self.cache[key]
            return None
        
        return item['url']
    
    def clean(self):
        now = time.time()
        expired = [k for k, v in self.cache.items() if now - v['time'] > Config.CACHE_TTL]
        for k in expired:
            del self.cache[k]
        return len(expired)

cache_manager = CacheManager()