from models.observation import Observation
from repositories.base import BaseMongoRepository
from typing import Optional, List
from bson import ObjectId

class ObservationRepository(BaseMongoRepository[Observation]):
    def __init__(self):
        super().__init__("observations", Observation)

    async def soft_delete_observation(self, session_id: str) -> bool:
        """Aplly the logic delete to the observation"""
        query = {"_id": ObjectId(session_id)}
        update_data = {"$set": {"deleted": True}}
        
        return await self.update_one(query, update_data)

    async def get_by_owner(self, owner_name: str, include_deleted: bool = False) -> List[Observation]:
        """Get all the user observations from the db"""
        query = {"owner": owner_name}
        
        if not include_deleted:
            query["deleted"] = {"$ne": True} 

        return await self.find_many(query)