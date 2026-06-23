import asyncio
import os
from core.logger import logger
from services.queue_manager import queue_manager
from services.downloader import InstagramDownloader

downloader = InstagramDownloader()

async def worker():
    while True:
        try:
            task = await queue_manager.get()
            
            client = task['client']
            status_msg = task['status_msg']
            url = task['url']
            quality = task['quality']
            user_id = task['user_id']
            
            logger.info(f"Worker started: {url} for user {user_id}")
            
            try:
                await status_msg.edit_text("⬇️ در حال دانلود...")
                
                result = await asyncio.to_thread(
                    downloader.download,
                    url,
                    quality
                )
                
                await status_msg.edit_text("⬆️ در حال ارسال به تلگرام...")
                
                if result['type'] == 'video':
                    thumb_path = result.get('thumbnail')
                    
                    await client.send_video(
                        chat_id=user_id,
                        video=result['path'],
                        caption="✅ دانلود شد",
                        supports_streaming=True,
                        thumb=thumb_path,
                        width=0,
                        height=0,
                        duration=0
                    )
                    
                    # پاک کردن تامبنیل بعد از ارسال
                    if thumb_path and os.path.exists(thumb_path):
                        try:
                            os.remove(thumb_path)
                            logger.info(f"Thumbnail removed: {thumb_path}")
                        except Exception as e:
                            logger.warning(f"Could not remove thumbnail: {e}")
                
                elif result['type'] == 'photo':
                    await client.send_photo(
                        chat_id=user_id,
                        photo=result['path'],
                        caption="✅ دانلود شد"
                    )
                
                elif result['type'] == 'audio':
                    await client.send_audio(
                        chat_id=user_id,
                        audio=result['path'],
                        caption="🎵",
                        performer="",
                        title=""
                    )
                
                else:
                    await client.send_document(
                        chat_id=user_id,
                        document=result['path'],
                        caption="✅ دانلود شد"
                    )
                
                # پاک کردن فایل اصلی
                try:
                    os.remove(result['path'])
                    logger.info(f"File removed: {result['path']}")
                except Exception as e:
                    logger.warning(f"Could not remove file: {e}")
                
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