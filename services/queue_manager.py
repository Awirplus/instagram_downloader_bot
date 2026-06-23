import asyncio

class QueueManager:
    def __init__(self):
        self.queue = asyncio.Queue()
    
    async def add(self, item):
        await self.queue.put(item)
    
    async def get(self):
        return await self.queue.get()
    
    def task_done(self):
        self.queue.task_done()
    
    def size(self):
        return self.queue.qsize()

queue_manager = QueueManager()