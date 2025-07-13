# src/scraper.py
import asyncio
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import json
import configparser
import os
from datetime import datetime, timedelta
from utils import logger, get_data_path, get_image_path
from dotenv import load_dotenv
from collections import defaultdict # To group messages by date
load_dotenv()
api_hash= os.getenv('APP_KEY')
api_id=os.getenv('APP_ID')
phone_number=os.getenv('PHONE')
config = configparser.ConfigParser()
config.read('config.ini')
async def scrape_telegram_channel(client, channel_entity, channel_name, channel_id, limit=None):
    """
    Asynchronously scrapes messages and media from a single Telegram channel.

    Args:
        client (telethon.sync.TelegramClient): The active and authenticated Telethon client instance.
        channel_entity (telethon.tl.types.Channel or telethon.tl.types.Chat): The Telethon entity object
                                                                                representing the target channel.
        channel_name (str): A human-readable name for the channel (e.g., its username or title).
                            Used for logging and file path creation.
        channel_id (str): A unique identifier for the channel, typically a key from the configuration.
                          Used to associate scraped data with the specific channel.
        limit (int, optional): The maximum number of messages to scrape. If None, scrapes all available messages.

    Returns:
        tuple: A tuple containing:
            - messages_by_date (defaultdict): A dictionary where keys are date strings (YYYY-MM-DD)
                                              and values are lists of message dictionaries scraped on that date.
            - channel_name (str): The normalized channel name used for file operations.
    """
    channel_name = getattr(channel_entity, 'username', getattr(channel_entity, 'title', 'unknown_channel')).replace('@', '')
    logger.info(f"Starting scraping for channel: {channel_name}")

    # Dictionary to store messages, grouped by date: { 'YYYY-MM-DD': [message_data_dict, ...] }
    messages_by_date = defaultdict(list)
    image_count = 0
    message_count = 0

    try:
        async for message in client.iter_messages(channel_entity, limit=limit):
            if not message.date:
                logger.warning(f"Message ID {message.id} in {channel_name} has no date. Skipping.")
                continue

            message_date_str = message.date.strftime('%Y-%m-%d')

            message_dict = {
                'id': message.id,
                'date': message.date.isoformat(),
                'message': message.message,
                'sender_id': message.sender_id,
                'views': message.views,
                'forwards': message.forwards,
                'replies': message.replies.replies if message.replies else None,
                'media_present': False,
                'media_type': None,
                'media_path': None,
                'channel_id': channel_name,
                'channel_name': channel_id 
            }

            if message.media:
                message_dict['media_present'] = True
                if isinstance(message.media, MessageMediaPhoto):
                    message_dict['media_type'] = 'photo'
                elif isinstance(message.media, MessageMediaDocument):
                    message_dict['media_type'] = 'document'
                    if message.media.document and message.media.document.mime_type and message.media.document.mime_type.startswith('image/'):
                        message_dict['media_type'] = 'image_document'

                if message_dict['media_type'] in ['photo', 'image_document']:
                    try:
                        file_ext = '.jpg'
                        if message_dict['media_type'] == 'image_document' and message.media.document.mime_type:
                            if 'png' in message.media.document.mime_type:
                                file_ext = '.png'
                            elif 'gif' in message.media.document.mime_type:
                                file_ext = '.gif'
                            elif 'jpeg' in message.media.document.mime_type:
                                file_ext = '.jpeg' # Ensure correct extension for JPEG

                        image_path = get_image_path(channel_name, message.date, message.id, file_ext)
                        await client.download_media(message, file=image_path)
                        message_dict['media_path'] = image_path
                        image_count += 1
                        logger.info(f"Downloaded image for message ID {message.id} (Date: {message_date_str}) to {image_path}")
                    except Exception as e:
                        logger.error(f"Error downloading media for message ID {message.id} (Date: {message_date_str}): {e}")
                else:
                    logger.info(f"Skipping non-image media for message ID {message.id} (Date: {message_date_str}, type: {message_dict['media_type']})")

            messages_by_date[message_date_str].append(message_dict)
            message_count += 1
            if message_count % 100 == 0:
                logger.info(f"Scraped {message_count} messages from {channel_name}...")

    except Exception as e:
        logger.error(f"Error scraping channel {channel_name}: {e}")

    logger.info(f"Finished scraping {message_count} messages and {image_count} images from {channel_name}.")
    return messages_by_date, channel_name


async def main():
    """
    Main asynchronous function to connect to Telegram, authenticate, and orchestrate
    the scraping of multiple configured Telegram channels. It saves scraped messages
    and downloads media to structured JSON files and image directories, respectively.

    Args:
        None

    Returns:
        None: The function performs operations (scraping, saving files) and does not
              return any value directly.
    """
    client = TelegramClient('channel_scraper', api_id, api_hash)
    
    logger.info("Connecting to Telegram...")
    await client.connect()

    if not await client.is_user_authorized():
        logger.info("Client not authorized. Sending authentication code...")
        await client.start(phone=phone_number)
        logger.info("Authentication successful.")

    channels_to_scrape = config.items('channels')
    
    for channel_key, channel_url_or_username in channels_to_scrape:
        try:
            entity = await client.get_entity(channel_url_or_username)
            channel_name_for_file = getattr(entity, 'username', getattr(entity, 'title', 'unknown_channel')).replace('@', '')

            # Scrape messages and images, grouped by date
            messages_by_date, _ = await scrape_telegram_channel(client, entity, channel_url_or_username, channel_key, 10)

            # Store raw data for each date
            for date_str, messages_on_date in messages_by_date.items():
                # Convert date_str back to datetime object for get_data_path if needed,
                # or modify get_data_path to accept string directly for date part.
                # For consistency with current utils.py, let's pass a dummy datetime object
                # for the `message_date` argument, specifically just for the date folder.
                # A more robust solution would be to make get_data_path take `date_str` directly.
                # For now, let's create a datetime object from date_str
                output_date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                
                output_filepath = get_data_path(channel_name_for_file, output_date_obj, "messages")
                
                # Check if file exists to append or create new
                existing_data = []
                if os.path.exists(output_filepath):
                    try:
                        with open(output_filepath, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                        # Filter out duplicates if re-running and appending
                        existing_ids = {msg['id'] for msg in existing_data}
                        new_messages_to_add = [msg for msg in messages_on_date if msg['id'] not in existing_ids]
                        all_messages = existing_data + new_messages_to_add
                    except json.JSONDecodeError:
                        logger.warning(f"Existing file {output_filepath} is not valid JSON. Overwriting.")
                        all_messages = messages_on_date
                else:
                    all_messages = messages_on_date

                with open(output_filepath, 'w', encoding='utf-8') as f:
                    json.dump(all_messages, f, ensure_ascii=False, indent=4)
                logger.info(f"Raw data for {channel_name_for_file} on {date_str} saved to {output_filepath}")

            # Add a delay to avoid rate limits
            await asyncio.sleep(5) # Wait for 5 seconds between channels

        except Exception as e:
            logger.error(f"Could not scrape {channel_url_or_username}: {e}")

    await client.disconnect()
    logger.info("Telegram client disconnected.")

if __name__ == "__main__":
    asyncio.run(main())