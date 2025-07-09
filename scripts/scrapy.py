import os
import pandas as pd
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import asyncio
load_dotenv()
APP_KEY = os.getenv('APP_KEY')
APP_ID = os.getenv('APP_ID')
PHONE = os.getenv('PHONE')
client = TelegramClient('channel_scraper', APP_ID, APP_KEY)
async def start_client():
    try:
        await client.start(phone=PHONE)
    except Exception as e:
        print(f'error has occured {e}')
async def get_entities( entity_name:str):
    try:
        print('here')
        await start_client()
        entity = await client.get_entity(entity_name)
        return entity
    except Exception as e:
        print(f"Failed to access {entity_name}: {e}")
        exit
async def get_messages( channel_name:str, limit:int=100):
    channel = await get_entities(channel_name)
    messages = []
    async for message in client.iter_messages(channel, limit=limit):
         messages.append({
            'message_id':message.id,
            'date': message.date,
            'sender_id': message.sender_id,
            'message': message.message,
            'views': message.views,
            'channel_name': channel_name
        });
    print(message)
    return messages
async def save_content( channel_names:list[str], limit:int=100):
    content = []
    print(channel_names)
    messages = []
    for channel in channel_names:
        try:
            messages = await get_messages(channel, limit)
        except Exception as e:
            print(e)
        content.append(pd.DataFrame(messages))
    
    df = pd.concat(content)
    df = df.dropna()
    df.to_csv('data/messages.csv')
        

async def main():
    await start_client()
    with open('channels.txt', 'r') as f:
        channel_list = [line.strip() for line in f.readlines()]
        await save_content(channel_list, 1000)         
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    

