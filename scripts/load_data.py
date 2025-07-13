import json
import os
import sys
sys.path.append('src')
import importlib
from db_manager import create_raw_table, load_raw_json
from database import DBConnection

def load_channel():
    """
    loads telegram messages to database
    """
    default_path = 'data/raw/telegram_messages/'
    message_folders = os.listdir(default_path)
    db = DBConnection()
    create_raw_table(db.connection)
    for folder in message_folders:
        for file in os.listdir(os.path.join(default_path, folder)):
            load_raw_json(conn=db.connection, file_path=os.path.join(default_path, folder, file))
              


if __name__ == "__main__":
    load_channel()