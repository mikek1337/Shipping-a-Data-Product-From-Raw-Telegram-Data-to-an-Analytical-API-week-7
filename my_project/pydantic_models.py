from pydantic import BaseModel, Field
from typing import Optional, Tuple, Any, List
from datetime import date
class ChannelActivities(BaseModel):
    ChannelId:str = Field(...,description='ID')
    NumberOfPosts: int = Field(...,description='ID')
    AverageView :int = Field(...,description='ID')
    PostFrequecy: int = Field(...,description='ID')
    @classmethod
    def from_db_tuple(cls, db_tuple: Tuple[Any, ...], column_names: List[str]):
        """
        Creates an Order instance from a database tuple and column names.
        """
        if len(db_tuple) != len(column_names):
            raise ValueError("Tuple length must match column names length.")

        data_dict = dict(zip(column_names, db_tuple))
        return cls(**data_dict)

class TelegramMessageResponse(BaseModel):
    """
    Pydantic model for a processed Telegram message,
    corresponding to the fct_messages table in the data warehouse.
    """
    message_id: int = Field(..., description="Unique identifier for the Telegram message.")
    message_text: Optional[str] = Field(None, description="The text content of the message.")
    sender_id: Optional[int] = Field(None, description="The ID of the sender of the message.")
    views: Optional[int] = Field(None, description="Number of views the message received.")
    forwards: Optional[int] = Field(None, description="Number of times the message was forwarded.")
    replies: Optional[int] = Field(None, description="Number of replies to the message.")
    media_present: bool = Field(..., description="Boolean indicating if media (photo, video, document) is present.")
    media_type: Optional[str] = Field(None, description="Type of media present (e.g., 'photo', 'image_document').")
    media_path: Optional[str] = Field(None, description="Local path where the media file is stored.")
    message_length: Optional[int] = Field(None, description="Length of the message text in characters.")
    has_image: bool = Field(..., description="Boolean indicating if the message contains an image.")
    channel_id: str = Field(..., description="Foreign key to the dim_channels table, identifying the channel.")
    date_id: date = Field(..., description="Foreign key to the dim_dates table, representing the message date.")

    @classmethod
    def from_db_tuple(cls, db_tuple: Tuple[Any, ...], column_names: List[str]):
        """
        Creates an Order instance from a database tuple and column names.
        """
        if len(db_tuple) != len(column_names):
            raise ValueError("Tuple length must match column names length.")

        data_dict = dict(zip(column_names, db_tuple))
        return cls(**data_dict)
    