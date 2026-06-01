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
