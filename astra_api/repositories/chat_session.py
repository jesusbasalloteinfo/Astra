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
Repository for managing chat session data in MongoDB.
"""
from pymongo import IndexModel, ASCENDING
from repositories.base import BaseMongoRepository
from models.chat_session import ChatSession

class ChatSessionRepository(BaseMongoRepository[ChatSession]):
    """
    Repository for ChatSession objects.

    Handles database operations for chat histories associated with observations.
    """
    def __init__(self):
        """Initializes the ChatSession repository."""
        super().__init__(collection_name="chat_sessions", model_class=ChatSession)

    async def setup_indexes(self):
        """
        Set up indexes for the chat_sessions collection.

        Creates an ascending index on 'observation_id'.
        """
        await super().setup_indexes()
        indexes = [
            IndexModel([("observation_id", ASCENDING)])
        ]
        await self.collection.create_indexes(indexes)
