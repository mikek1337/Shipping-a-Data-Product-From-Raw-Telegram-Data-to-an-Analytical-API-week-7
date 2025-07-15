# src/utils.py
import logging
import os
from datetime import datetime

def setup_logging():
    """
    Sets up the logging configuration for the application.
    It creates a 'logs' directory if it doesn't exist, configures a file handler
    to write logs to 'scraper.log', and also sets up a stream handler to output
    logs to the console. The log level is set to INFO.

    Args:
        None

    Returns:
        logging.Logger: A configured logger instance for the current module.
    """
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
    """
    Generates a file path for storing raw data (e.g., messages) for a specific channel
    on a given date. It ensures the necessary directory structure exists.

    Args:
        channel_name (str): The name of the Telegram channel.
        message_date (datetime): A datetime object representing the date of the messages.
                                 This date is used to create a YYYY-MM-DD subfolder.
        data_type (str, optional): The type of data being stored, which influences the
                                   base directory name (e.g., 'messages', 'documents').
                                   Defaults to "messages".

    Returns:
        str: The full file path (including directory and filename) where the data
             should be saved (e.g., 'data/raw/telegram_messages/2023-10-27/my_channel.json').
    """
    # Format the message date as YYYY-MM-DD
    date_str = message_date.strftime('%Y-%m-%d')
    base_path = f'../data/raw/telegram_{data_type}/{date_str}'
    os.makedirs(base_path, exist_ok=True)
    return os.path.join(base_path, f'{channel_name}.json')

def get_image_path(channel_name, message_date, message_id, file_extension):
    """
    Generates a file path for storing downloaded image files for a specific message
    from a given channel on a particular date. It ensures the necessary directory
    structure exists.

    Args:
        channel_name (str): The name of the Telegram channel.
        message_date (datetime): A datetime object representing the date the message
                                 was sent. This date is used to create a YYYY-MM-DD subfolder.
        message_id (int): The unique ID of the Telegram message from which the image
                          was downloaded. This ID is used as part of the image filename.
        file_extension (str): The file extension for the image (e.g., '.jpg', '.png', '.gif').

    Returns:
        str: The full file path (including directory and filename) where the image
             should be saved (e.g., 'data/raw/telegram_images/2023-10-27/my_channel/12345.jpg').
    """
    # Format the message date as YYYY-MM-DD
    date_str = message_date.strftime('%Y-%m-%d')
    base_path = f'../data/raw/telegram_images/{date_str}/{channel_name}'
    os.makedirs(base_path, exist_ok=True)
    return os.path.join(base_path, f'{message_id}{file_extension}')