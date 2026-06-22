import asyncio
import os
from core.logger import logger
from services.queue_manager import queue_manager
from services.downloader import InstagramDownloader

downloader = InstagramDownloader()

async def worker():
    """پردازش‌کننده صف دانلود"""
    
    while True:
        try:
            # دریافت از صف
            task = await queue_manager.get()
            
            client = task['client']
            status_msg = task['status_msg']
            url = task['url']
            quality = task['quality']
            user_id = task['user_id']
            
            logger.info(f"Worker started: {url} for user {user_id}")
            
            try:
                # به‌روزرسانی وضعیت
                await status_msg.edit_text("⬇️ در حال دانلود...")
                
                # دانلود (اجرا در ترد جداگانه)
                result = await asyncio.to_thread(
                    downloader.download,
                    url,
                    quality
                )
                
                # ارسال فایل
                await status_msg.edit_text("⬆️ در حال ارسال به تلگرام...")
                
                if result['type'] == 'video':
                    await client.send_video(
                        chat_id=user_id,
                        video=result['path'],
                        caption=f"✅ دانلود شد | کیفیت: {quality}",
                        supports_streaming=True
                    )
                elif result['type'] == 'photo':
                    await client.send_photo(
                        chat_id=user_id,
                        photo=result['path'],
                        caption=f"✅ دانلود شد | کیفیت: {quality}"
                    )
                else:
                    await client.send_document(
                        chat_id=user_id,
                        document=result['path'],
                        caption=f"✅ دانلود شد | کیفیت: {quality}"
                    )
                
                # پاکسازی فایل
                try:
                    os.remove(result['path'])
                    logger.info(f"File removed: {result['path']}")
                except:
                    pass
                
                # حذف پیام وضعیت
                await status_msg.delete()
                
                logger.info(f"Download complete for user {user_id}")
                
            except Exception as e:
                logger.error(f"Download error: {e}")
                await status_msg.edit_text(f"❌ خطا در دانلود:\n{str(e)}")
            
            finally:
                queue_manager.task_done()
                
        except Exception as e:
            logger.error(f"Worker error: {e}")
            await asyncio.sleep(1)