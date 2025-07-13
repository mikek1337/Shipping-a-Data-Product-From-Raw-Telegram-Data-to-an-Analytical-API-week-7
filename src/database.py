import psycopg2
import os
import sys
from datetime import datetime
sys.path.append('scripts')
from utils import logger
from dotenv import load_dotenv
load_dotenv()
class DBConnection:
    """
    Manages connections and operations with a PostgreSQL database.
    It encapsulates connection details, connection testing, and methods
    for inserting and querying data related to Telegram channels, messages, and images.
    """
    def __init__(self):
        """
        Initializes the DBConnection object by loading database credentials from
        environment variables and establishing a connection to the PostgreSQL database.

        Args:
            None

        Returns:
            None
        """
        self.host = os.getenv('HOST')
        self.port = os.getenv('PORT')
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        self.database = os.getenv('DATABASE')
        self.connection = self.get_connection(self.host, self.port, self.username,self.password,self.database)
    def get_connection(self, host:str='localhost', port:int=5432, username:str='postgres',password:str='',database:str='raw_telegram'):
        """
        Establishes and returns a connection to a PostgreSQL database.

        Args:
            host (str): The database host address. Defaults to 'localhost'.
            port (int): The database port number. Defaults to 5432.
            username (str): The username for database authentication. Defaults to 'postgres'.
            password (str): The password for database authentication. Defaults to an empty string.
            database (str): The name of the database to connect to. Defaults to 'raw_telegram'.

        Returns:
            psycopg2.connection or None: A psycopg2 connection object if successful,
                                         None if an error occurs during connection.
        """
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
        """
        Tests if the current database connection is active and valid.

        Args:
            None

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        print(self.connection)
        if self.connection != None:
            print('Connected successfully')
            return True
        else:
            print("Connection faliure")
            return False
    def insert_channel(self, channel_name:str):
        """
        Inserts a new channel into the 'channels' table or updates it if a conflict
        (based on 'channel_name') occurs. This ensures channel names are unique.

        Args:
            channel_name (str): The name of the channel to insert or update.

        Returns:
            None: The function performs a database operation and commits it.
        """
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
        """
        Inserts or updates a message record in the 'messages' table. If the message
        contains relevant media (photo or image document), it also inserts or updates
        an associated record in the 'images' table. Handles type conversions and conflicts.

        Args:
            message_data (dict): A dictionary containing message details, typically scraped
                                 from Telegram. Expected keys include 'id', 'channel_id',
                                 'message', 'date', 'sender_id', 'views', 'forwards',
                                 'replies', 'media_present', 'media_type', 'media_path'.

        Returns:
            None: The function performs database operations and commits them.
        """
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
            """
        Retrieves the ID of a channel from the 'channels' table based on its name.

        Args:
            channel_name (str): The name of the channel to search for.

        Returns:
            tuple or None: A tuple containing the channel ID if found, otherwise None.
                           Returns a tuple like (ID,)
        """
            sql_insert = """
            SELECT ID FROM channels WHERE channel_name=%s;
            """
            
            cur = self.connection.cursor()
            print(sql_insert)
            cur.execute(sql_insert, (channel_name))
            return cur.fetchone()
    def insert(self, table_name:str, data:dict):
            """
        Inserts a single row of data into a specified table.
        Note: This is a generic insert method that constructs SQL dynamically.
              It is less safe against SQL injection if 'data' comes from untrusted sources
              and should be used with caution, or preferably, by using parameterized queries.
              The current implementation has basic type handling for strings/non-strings.

        Args:
            table_name (str): The name of the table to insert into.
            data (dict): A dictionary where keys are column names and values are the
                         data to be inserted for those columns.

        Returns:
            None: The function performs a database operation and commits it.
        """
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
        """
        Retrieves all columns from a specified table, optionally filtered by a WHERE clause.
        Note: This method is susceptible to SQL injection if 'where' comes directly from
              user input without proper sanitization or parameterization.

        Args:
            table_name (str): The name of the table to query.
            where (str, optional): A SQL WHERE clause (e.g., "column = 'value'").
                                   Defaults to an empty string, meaning no WHERE clause.

        Returns:
            list or None: A list of tuples, where each tuple represents a row from the
                          query result. Returns None if an error occurs.
        """
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