"""
Models for chat sessions in astra_api.
"""
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

from services.assistant.models import ChatMessage

class ChatSession(BaseModel):
    """
    Model representing a chat session between a user and the AI assistant.

    Attributes:
        id (Optional[str]): The unique identifier for the session (MongoDB ID).
        observation_id (str): The ID of the observation associated with this chat.
        title (str): The display title for the chat session.
        messages (List[ChatMessage]): The list of messages in the chat history.
        created_at (datetime): The timestamp when the session was created.
        updated_at (datetime): The timestamp of the last update to the session.
    """
    id: Optional[str] = Field(alias="_id", default=None)
    observation_id: str
    title: str = "Default Chat"
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {"populate_by_name": True}
