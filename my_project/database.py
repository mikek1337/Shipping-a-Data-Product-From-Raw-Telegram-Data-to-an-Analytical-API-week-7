import psycopg2
import os
import sys
from datetime import datetime
from pydantic_models import TelegramMessageResponse, ChannelActivities
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
        """
        Searches for Telegram messages containing a specific text query within the
        'raw.fct_messages' table.

        This function performs a LIKE search on the 'message_text' column.

        Args:
            query (str): The text string to search for within message content.
                         It should include SQL LIKE wildcards if desired (e.g., '%keyword%', 'start%').

        Returns:
            list[TelegramMessageResponse]: A list of TelegramMessageResponse objects
                                          representing messages that match the query.
                                          Each object contains details like message_id,
                                          message_text, views, etc.
        """
        curr = self.connection.cursor()
        curr.execute("SELECT * FROM raw.fct_messages WHERE message_text LIKE %s;", (query,))
        result = curr.fetchall()
        message_responses = []
        for rs in result:
            message_responses.append(TelegramMessageResponse.from_db_tuple(rs,['message_id', 'message_text', 'sender_id', 'views', 'forwards', 'replies', 'media_present', 'media_type', 'media_path', 'message_length', 'has_image', 'channel_id', 'date_id']))
        return message_responses
    def top_products(self, limit:int):
        """
        Retrieves messages that are considered "top products" based on a simple
        heuristic: messages with at least one forward.

        Note: The current implementation retrieves all messages with forwards > 0
              and does not apply the 'limit' parameter from the function signature
              in the SQL query. To truly limit the results, the SQL query
              would need a 'LIMIT %s' clause.

        Args:
            limit (int): The maximum number of top product messages to retrieve.
                         (Currently not applied in the SQL query, all matching
                         messages are fetched).

        Returns:
            list[TelegramMessageResponse]: A list of TelegramMessageResponse objects
                                          representing messages that have been forwarded.
        """
        curr = self.connection.cursor()
        sql = "SELECT * FROM raw.fct_messages WHERE forwards > 0"
        curr.execute(sql)
        result = curr.fetchall()
        message_responses = []
        for rs in result:
            message_responses.append(TelegramMessageResponse.from_db_tuple(rs,['message_id', 'message_text', 'sender_id', 'views', 'forwards', 'replies', 'media_present', 'media_type', 'media_path', 'message_length', 'has_image', 'channel_id', 'date_id']))
        return message_responses
    def channel_activity(self, channel_name:str):
        """
        Calculates key activity metrics for a specific Telegram channel.

        Metrics include Average View per post, Total Number of Posts, and Post Frequency.
        The calculation is grouped by date and channel, and ordered by date.

        Args:
            channel_name (str): The ID of the channel for which to calculate activity.
                                This is expected to correspond to `dim_channels.channel_id`.

        Returns:
            ChannelActivities: An object containing the calculated activity metrics
                               for the specified channel, including ChannelId,
                               NumberOfPosts, AverageView, and PostFrequency.
                               Returns None if no activity is found for the channel.
        """
        curr = self.connection.cursor()
        sql = """SELECT
        fct_messages.channel_id,
        CAST(SUM(CASE WHEN dim_channels.channel_id = %s THEN fct_messages.views ELSE 0 END) AS DECIMAL) / COUNT(CASE WHEN dim_channels.channel_id = %s THEN fct_messages.message_id END) AS AverageView,
        COUNT(CASE WHEN dim_channels.channel_id = %s THEN fct_messages.message_id END) AS TotalNumberOfPosts,
        COUNT(fct_messages.message_text) AS PostFrequency
        FROM
        raw.dim_channels
        INNER JOIN
            raw.fct_messages ON raw.dim_channels.channel_id = raw.fct_messages.channel_id
        WHERE
            dim_channels.channel_id = %s
        GROUP BY
            raw.fct_messages.date_id, raw.fct_messages.channel_id
        ORDER BY
            raw.fct_messages.date_id ASC;"""
        curr.execute(sql, (channel_name,channel_name,channel_name,channel_name))
        result = curr.fetchone()
        return ChannelActivities.from_db_tuple(result,['ChannelId', 'NumberOfPosts', 'AverageView', 'PostFrequecy'])

        
    

        
 