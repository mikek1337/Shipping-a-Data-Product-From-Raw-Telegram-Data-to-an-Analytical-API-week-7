from fastapi import FastAPI, status
import os
from typing import Union, List
from database import DBConnection
from pydantic_models import ChannelActivities,TelegramMessageResponse
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
db = DBConnection(os.getenv('HOST'), os.getenv('PORT'), os.getenv('USERNAME'), os.getenv('PASSWORD'), os.getenv('DATABASE'))


@app.get('/reports/top-products', response_model=List[TelegramMessageResponse], status_code=status.HTTP_200_OK,
         summary="Retrieve a list of top-performing product messages",
         description="""
         This endpoint fetches Telegram messages identified as "top products".
         Currently, "top products" are defined as messages that have received at least one forward.
         The `limit` parameter is provided but is not currently applied in the underlying SQL query;
         all messages matching the 'forwards > 0' criterion will be returned.
         """)
def get_top_products(limit:Union[int, None]=10):
    """
    Retrieves a list of top-performing product messages from the database.

    Args:
        limit (int, optional): The maximum number of top product messages to return.
                               Defaults to 10. Note: The current database function
                               `db.top_products` does not apply this limit in its
                               SQL query, meaning all qualifying messages are fetched.

    Returns:
        List[TelegramMessageResponse]: A list of TelegramMessageResponse objects,
                                       each representing a top product message.

    Raises:
        HTTPException: If there's an issue with the database connection (though
                       not explicitly handled in the provided snippet).
    """
    return db.top_products(limit)

@app.get('/channels/{channel_name}/activity', 
         response_model=ChannelActivities, status_code=status.HTTP_200_OK,summary="Get activity metrics for a specific channel",
         description="""
         This endpoint provides aggregated activity metrics for a given Telegram channel,
         including average views per post, total number of posts, and post frequency.
         """)
def get_channel_activity(channel_name:str):
    """
    Retrieves activity metrics for a specified Telegram channel.

    Args:
        channel_name (str): The unique identifier (ID) of the channel
                            for which to retrieve activity data.

    Returns:
        ChannelActivities: An object containing the calculated activity metrics
                           for the specified channel.

    Raises:
        HTTPException: If the channel is not found or if there's a database error.
                       (The provided `db.channel_activity` returns None if not found,
                       which would need to be handled here, e.g., raising 404).
    """
    return db.channel_activity(channel_name)
@app.get('/search/messages', response_model=List[TelegramMessageResponse], status_code=status.HTTP_200_OK,summary="Search Telegram messages by text query",
    description="""
    This endpoint allows searching for Telegram messages based on a text query.
    The search is performed using a LIKE operator on the message content,
    so you can use SQL wildcards (e.g., '%' for any sequence of characters)
    within your query.
    """)
def search_messages(query:Union[str, None]=None):
    """
    Searches for Telegram messages based on a provided text query.

    Args:
        query (str, optional): The text query to search for within message content.
                               If not provided, or if the database connection fails,
                               an empty list will be returned. The query will be
                               wrapped with '%' wildcards (e.g., "keyword" becomes "%keyword%").

    Returns:
        List[TelegramMessageResponse]: A list of TelegramMessageResponse objects
                                       matching the search query. Returns an empty
                                       list if no query is provided or if the
                                       database connection fails.

    Raises:
        HTTPException: If the database connection fails (implicitly handled by
                       returning an empty list in the current logic, but could
                       be made explicit with a 500 error).
    """
    if db.test_connection() and query != None:
        return db.search_message(f"%{query}%")
        