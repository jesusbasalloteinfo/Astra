"""
Service for managing chat session business logic in astra_api.
"""
from typing import List
from datetime import datetime, timezone
from bson import ObjectId

from models.chat_session import ChatSession
from repositories.chat_session import ChatSessionRepository
from services.assistant.models import ChatMessage
from services.db.ObservationService import ObservationService
from core.db_exceptions import ObjectNotFoundError

class ChatSessionService:
    """
    Service to coordinate chat session operations between repositories and observations.
    """
    def __init__(self):
        """Initializes the ChatSession service."""
        self.repo = ChatSessionRepository()
        self.obs_service = ObservationService()

    async def get_or_create_session(self, observation_id: str, username: str) -> ChatSession:
        """
        Gets the active chat session for an observation, or creates a default one.

        Verifies that the user owns the observation before returning or creating
         the session.

        Args:
            observation_id (str): The identifier of the observation.
            username (str): The username of the requestor.

        Returns:
            ChatSession: The existing or newly created chat session.

        Raises:
            ObjectNotFoundError: If the observation does not exist or is not owned by the user.
        """
        # This will raise ObjectNotFoundError if the user doesn't own it or it doesn't exist
        await self.obs_service.get_observation(observation_id, username)

        # Right now we assume 1 chat per observation, so we just get the first one.
        sessions = await self.repo.find_many({"observation_id": observation_id})
        
        if sessions:
            return sessions[0]
        
        # Create a new session
        new_session = ChatSession(
            observation_id=observation_id,
            title="Default Chat"
        )
        session_id = await self.repo.insert_one(new_session)
        new_session.id = session_id
        return new_session

    async def get_session(self, session_id: str, username: str) -> ChatSession:
        """
        Get a chat session by ID and verify ownership of the associated observation.

        Args:
            session_id (str): The unique identifier of the chat session.
            username (str): The username of the requestor.

        Returns:
            ChatSession: The chat session instance.

        Raises:
            ObjectNotFoundError: If the session does not exist or access is denied.
        """
        session = await self.repo.find_one({"_id": ObjectId(session_id)})
        if not session:
            raise ObjectNotFoundError(f"ChatSession with id {session_id} not found")
        
        # Verify ownership
        await self.obs_service.get_observation(session.observation_id, username)
        
        return session

    async def save_messages(self, session_id: str, messages: List[ChatMessage]) -> bool:
        """
        Updates the messages array for a given session.

        Args:
            session_id (str): The identifier of the chat session.
            messages (List[ChatMessage]): The full list of messages to save.

        Returns:
            bool: True if the session was updated, False otherwise.
        """
        update_data = {
            "messages": [msg.model_dump(exclude_none=True) for msg in messages],
            "updated_at": datetime.now(timezone.utc)
        }
        
        return await self.repo.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": update_data}
        )
