import psycopg2
import os
import sys
from datetime import datetime
sys.path.append('scripts')
from utils import logger
from dotenv import load_dotenv
load_dotenv()
class DBConnection:
    def __init__(self):
        self.host = os.getenv('HOST')
        self.port = os.getenv('PORT')
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        self.database = os.getenv('DATABASE')
        self.connection = self.get_connection(self.host, self.port, self.username,self.password,self.database)
    def get_connection(self, host:str='localhost', port:int=5432, username:str='postgres',password:str='',database:str='raw_telegram'):
        try:
            return psycopg2.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=database
            )
        except:
            print(f'error ')
            return None
    def test_connection(self):
        print(self.connection)
        if self.connection != None:
            print('Connected successfully')
            return True
        else:
            print("Connection faliure")
            return False
    def insert_channel(self, channel_name:str):
        """Inserts or updates channel information."""
        sql_insert = """
            INSERT INTO channels (channel_name)
            VALUES (%s) ON CONFLICT (channel_name) DO UPDATE SET
            channel_name = EXCLUDED.channel_name;
        """
        try:
            cur = self.connection.cursor()
            cur.execute(sql_insert, (channel_name))
            self.connection.commit()
            logger.info(f"Channel ({channel_name}) inserted/updated.")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error inserting/updating channel ({channel_name}): {e}")
    def insert_message(self, message_data):
        """Inserts or updates a message and its associated image (if any)."""
        sql_insert_message = """
            INSERT INTO messages (id, channel_id, message_text, message_date, sender_id, 
                                views, forwards, replies, media_present, media_type, media_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                channel_id = EXCLUDED.channel_id,
                message_text = EXCLUDED.message_text,
                message_date = EXCLUDED.message_date,
                sender_id = EXCLUDED.sender_id,
                views = EXCLUDED.views,
                forwards = EXCLUDED.forwards,
                replies = EXCLUDED.replies,
                media_present = EXCLUDED.media_present,
                media_type = EXCLUDED.media_type,
                media_path = EXCLUDED.media_path,
                scraped_at = NOW();
        """
        sql_insert_image = """
            INSERT INTO images (message_id, channel_id, image_path)
            VALUES (%s, %s, %s)
            ON CONFLICT (message_id) DO UPDATE SET
                image_path = EXCLUDED.image_path,
                scraped_at = NOW();
        """
        try:
            cur = self.connection.cursor()
            
            # Convert date string to datetime object with timezone awareness
            message_date_obj = datetime.fromisoformat(message_data['date'])
            
            # Defensive type conversion for potentially None or unexpected types
            views_val = message_data.get('views')
            if views_val is not None and not isinstance(views_val, int):
                try:
                    views_val = int(views_val)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert views value '{views_val}' to integer for message ID {message_data.get('id')}. Setting to None.")
                    views_val = None

            forwards_val = message_data.get('forwards')
            if forwards_val is not None and not isinstance(forwards_val, int):
                try:
                    forwards_val = int(forwards_val)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert forwards value '{forwards_val}' to integer for message ID {message_data.get('id')}. Setting to None.")
                    forwards_val = None

            replies_val = message_data.get('replies')
            if replies_val is not None and not isinstance(replies_val, int):
                try:
                    replies_val = int(replies_val)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert replies value '{replies_val}' to integer for message ID {message_data.get('id')}. Setting to None.")
                    replies_val = None

            cur.execute(sql_insert_message, (
                message_data.get('id'), # Use .get() for safety, though scraper should ensure presence
                message_data.get('channel_id'),
                message_data.get('message'),
                message_date_obj,
                message_data.get('sender_id'),
                views_val, # Use the potentially converted value
                forwards_val, # Use the potentially converted value
                replies_val, # Use the potentially converted value
                message_data.get('media_present'),
                message_data.get('media_type'),
                message_data.get('media_path')
            ))

            if message_data['media_present'] and message_data['media_path'] and \
            (message_data['media_type'] == 'photo' or message_data['media_type'] == 'image_document'):
                cur.execute(sql_insert_image, (
                    message_data.get('id'),
                    message_data.get('channel_id'),
                    message_data.get('media_path')
                ))
            self.connection.commit()
            logger.debug(f"Message ID {message_data.get('id')} inserted/updated.")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error inserting/updating message ID {message_data.get('id')}: {e}")
        finally:
            if 'cur' in locals() and cur:
                cur.close()
    def find_channel(self,channel_name:str):
            sql_insert = """
            SELECT ID FROM channels WHERE channel_name=%s;
            """
            
            cur = self.connection.cursor()
            print(sql_insert)
            cur.execute(sql_insert, (channel_name))
            return cur.fetchone()
    def insert(self, table_name:str, data:dict):
            cols = data.keys()
            curr =  self.connection.cursor()
            col_names = ','.join(cols)
            content = ''
            for col in cols:
                if type(data[col]) == str:
                    content+= f"'{data[col]}',"
                else:
                    content+= f"{data[col]},"
            content = content.removesuffix(',')
            
            curr.execute(f'INSERT INTO {table_name} ({col_names}) VALUES ({content})')
                
    def get(self, table_name, where:str=''):
        try:
            curr = self.connection.cursor()
            if where != None or where != '':
                curr.execute(f'SELECT * FROM {table_name} WHERE {where};')
            else:
                curr.execute(f'SELECT * FROM {table_name};')
            
            return curr.fetchall()
        except:
            return None
        #curr = self.connection.cursor(f'INSERT INTO {table_name} VALUES {}')
if __name__ == "__main__":
    db = DBConnection()
    db.test_connection()