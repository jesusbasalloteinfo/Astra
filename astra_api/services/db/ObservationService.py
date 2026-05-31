"""
Service for managing astronomical observation business logic in astra_api.
"""
from typing import List, Optional

from bson import ObjectId
from models.observation import Observation
from repositories.observation import ObservationRepository
from core.db_exceptions import ObjectAlreadyExistsError, ObjectNotFoundError, ObjectFailureError

class ObservationService:
    """
    Service to coordinate observation creation, retrieval, and management.
    """
    def __init__(self):
        """Initializes the Observation service."""
        self.repo = ObservationRepository()

    async def create_observation(self, data: Observation) -> str:
        """
        Creates a new observation in the database.

        Checks if an observation with the same name already exists for the user.

        Args:
            data (Observation): The observation data model.

        Returns:
            str: The identifier of the created observation.

        Raises:
            ObjectAlreadyExistsError: If an observation with the same name exists.
        """
        # Check if name duplicate in user's observations
        exists = await self.repo.find_one({"name": data.name, "owner": data.owner})
        if exists:
            raise ObjectAlreadyExistsError(f"Observation '{data.name}' already exists for this user")
        
        # Clean incoming id 
        data.id = None
        return await self.repo.insert_one(data)

    async def get_observation(self, obs_id: str, user: str) -> Observation:
        """
        Retrieves a specific observation by ID, ensuring user ownership.

        Args:
            obs_id (str): The observation identifier.
            user (str): The username of the requestor.

        Returns:
            Observation: The observation instance.

        Raises:
            ObjectNotFoundError: If the observation doesn't exist, is deleted, or is not owned by the user.
        """
        observation = await self.repo.find_one({"_id": ObjectId(obs_id)})
        if not observation or observation.deleted or observation.owner != user:
            raise ObjectNotFoundError(f"Observation with id {obs_id} not found")
        return observation

    async def get_owner_observations(self, owner: str) -> List[Observation]:
        """
        Retrieves all active observations belonging to a user.

        Args:
            owner (str): The username of the owner.

        Returns:
            List[Observation]: A list of non-deleted observations.
        """
        return await self.repo.get_by_owner(owner)

    async def update_observation_info(self, obs_id: str, user: str, **update_data) -> bool:
        """
        Updates fields for a specific observation.

        Args:
            obs_id (str): The observation identifier.
            user (str): The username of the requestor.
            **update_data: The fields and values to update.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            ObjectNotFoundError: If access is denied or the observation is not found.
        """
        await self.get_observation(obs_id, user) # Checks ownership

        # Clean None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if not update_data:
            return False

        return await self.repo.update_one(
            {"_id": ObjectId(obs_id)},
            {"$set": update_data}
        )


    async def delete_observation(self, obs_id: str, user: str) -> bool:
        """
        Soft-deletes an observation.

        Args:
            obs_id (str): The identifier of the observation to delete.
            user (str): The username of the owner.

        Returns:
            bool: True if the soft-delete was successful.

        Raises:
            ObjectNotFoundError: If access is denied or the observation is not found.
        """
        await self.get_observation(obs_id, user) # Checks ownership

        return await self.repo.soft_delete_observation(obs_id)
