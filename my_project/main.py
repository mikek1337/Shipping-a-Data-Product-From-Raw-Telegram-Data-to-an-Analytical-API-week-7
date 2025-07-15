from fastapi import FastAPI, status
import os
from typing import Union
from database import DBConnection
from pydantic_models import ChannelActivities,TelegramMessageResponse
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
db = DBConnection(os.getenv('HOST'), os.getenv('PORT'), os.getenv('USERNAME'), os.getenv('PASSWORD'), os.getenv('DATABASE'))


@app.get('/reports/top-products')
def get_top_products(limit:Union[int, None]=None):
    return {"limit":limit}

@app.get('/channels/{channel_name}/activity', response_model=ChannelActivities, status_code=status.HTTP_200_OK)
def get_channel_activity(channel_name:str):
    return {'channel':channel_name}
@app.get('/search/messages')
def search_messages(query:Union[str, None]=None):
    if db.test_connection() and query != None:
        return db.search_message(f"%{query}%")
        