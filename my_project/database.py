import psycopg2
import os
import sys
from datetime import datetime
from pydantic_models import TelegramMessageResponse
sys.path.append('../scripts')
from utils import logger

class DBConnection:
    """
    Manages connections and operations with a PostgreSQL database.
    It encapsulates connection details, connection testing, and methods
    for inserting and querying data related to Telegram channels, messages, and images.
    """
    def __init__(self, host:str, port:int, username:str,password:str,database:str):
        """
        Initializes the DBConnection object by loading database credentials from
        environment variables and establishing a connection to the PostgreSQL database.

        Args:
            None

        Returns:
            None
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
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
    
    def search_message(self, query:str):
        curr = self.connection.cursor()
        curr.execute("SELECT * FROM raw_analytics.fct_messages WHERE message_text LIKE %s;", (query,))
        result = curr.fetchall()
        message_responses = []
        for rs in result:
            message_responses.append(TelegramMessageResponse.from_db_tuple(rs,['message_id', 'message_text', 'sender_id', 'views', 'forwards', 'replies', 'media_present', 'media_type', 'media_path', 'message_length', 'has_image', 'channel_id', 'date_id']))
        return message_responses
    def top_products(self, limit:int):
        curr = self.connection.cursor()
        sql = "SELECT * FROM raw_analytics.fct_messages WHERE forward > 0"
        result = curr.fetchmany(limit)
        message_responses = []
        for rs in result:
            message_responses.append(TelegramMessageResponse.from_db_tuple(rs,['message_id', 'message_text', 'sender_id', 'views', 'forwards', 'replies', 'media_present', 'media_type', 'media_path', 'message_length', 'has_image', 'channel_id', 'date_id']))
        return message_responses

        
 