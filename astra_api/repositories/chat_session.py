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
