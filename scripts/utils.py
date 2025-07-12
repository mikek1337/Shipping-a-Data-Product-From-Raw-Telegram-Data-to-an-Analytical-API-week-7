# src/utils.py
import logging
import os
from datetime import datetime

def setup_logging():
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'scraper.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Removed get_today_date_str() as it's no longer used for data path

def get_data_path(channel_name, message_date, data_type="messages"):
    # Format the message date as YYYY-MM-DD
    date_str = message_date.strftime('%Y-%m-%d')
    base_path = f'data/raw/telegram_{data_type}/{date_str}'
    os.makedirs(base_path, exist_ok=True)
    return os.path.join(base_path, f'{channel_name}.json')

def get_image_path(channel_name, message_date, message_id, file_extension):
    # Format the message date as YYYY-MM-DD
    date_str = message_date.strftime('%Y-%m-%d')
    base_path = f'data/raw/telegram_images/{date_str}/{channel_name}'
    os.makedirs(base_path, exist_ok=True)
    return os.path.join(base_path, f'{message_id}{file_extension}')