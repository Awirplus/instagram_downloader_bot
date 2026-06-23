import logging
import sys
import os

os.makedirs("logs", exist_ok=True)

def setup_logger():
    logger = logging.getLogger("InstaBot")
    logger.setLevel(logging.INFO)
    
    # خروجی در ترمینال
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(handler)
    
    # خروجی در فایل با encoding=utf-8
    file_handler = logging.FileHandler("logs/bot.log", encoding='utf-8')
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()