"""
Repository for managing astronomical observation data in MongoDB.
"""
from models.observation import Observation
from repositories.base import BaseMongoRepository
from typing import Optional, List
from bson import ObjectId

class ObservationRepository(BaseMongoRepository[Observation]):
    """
    Repository for Observation objects.

    Handles creation, soft deletion, and retrieval of observation sessions.
    """
    def __init__(self):
        """Initializes the Observation repository."""
        super().__init__("observations", Observation)

    async def soft_delete_observation(self, session_id: str) -> bool:
        """
        Apply logical deletion to an observation.

        Args:
            session_id (str): The identifier of the observation to delete.

        Returns:
            bool: True if the observation was updated, False otherwise.
        """
        query = {"_id": ObjectId(session_id)}
        update_data = {"$set": {"deleted": True}}
        
        return await self.update_one(query, update_data)

    async def get_by_owner(self, owner_name: str, include_deleted: bool = False) -> List[Observation]:
        """
        Retrieve all observations belonging to a specific user.

        Args:
            owner_name (str): The username of the owner.
            include_deleted (bool): Whether to include observations marked as deleted.

        Returns:
            List[Observation]: A list of observation instances.
        """
        query = {"owner": owner_name}
        
        if not include_deleted:
            query["deleted"] = {"$ne": True} 

        return await self.find_many(query)
