"""
ASTRA - Automated Smart Telescope Remote Assistant
Copyright (C) 2026 Jesus Basallote

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
