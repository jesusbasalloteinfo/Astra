from pymongo import IndexModel, ASCENDING
from repositories.base import BaseMongoRepository
from models.chat_session import ChatSession

class ChatSessionRepository(BaseMongoRepository[ChatSession]):
    def __init__(self):
        super().__init__(collection_name="chat_sessions", model_class=ChatSession)

    async def setup_indexes(self):
        """Set up indexes for the chat_sessions collection"""
        await super().setup_indexes()
        indexes = [
            IndexModel([("observation_id", ASCENDING)])
        ]
        await self.collection.create_indexes(indexes)
