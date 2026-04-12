from typing import List, Optional

from bson import ObjectId
from models.observation import Observation
from repositories.observation import ObservationRepository
from core.db_exceptions import ObjectAlreadyExistsError, ObjectNotFoundError, ObjectFailureError

class ObservationService:
    def __init__(self):
        self.repo = ObservationRepository()

    async def create_observation(self, data: Observation) -> str:
        """ Creates an observation in db """
        # Check if name duplicate in user's observations
        exists = await self.repo.find_one({"name": data.name, "owner": data.owner})
        if exists:
            raise ObjectAlreadyExistsError(f"Observation '{data.name}' already exists for this user")
        
        # Clean incoming id 
        data.id = None
        return await self.repo.insert_one(data)

    async def get_observation(self, obs_id: str, user:str) -> Observation:
        """ Get an observation from the db """
        observation = await self.repo.find_one({"_id": ObjectId(obs_id)})
        if not observation or observation.deleted or observation.owner != user:
            raise ObjectNotFoundError(f"Observation with id {obs_id} not found")
        return observation

    async def get_owner_observations(self, owner: str) -> List[Observation]:
        """ Get all user observations """
        return await self.repo.get_by_owner(owner)

    async def update_observation_info(self, obs_id: str, user: str, **update_data) -> bool:
        """Update only the fields provided of the observation"""
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
        """Soft-deletes a user observation"""
        await self.get_observation(obs_id, user) # Checks ownership

        return await self.repo.soft_delete_observation(obs_id)
        