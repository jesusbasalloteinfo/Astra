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
Repository for managing user profile data in MongoDB.
"""
from models.user import User
from repositories.base import *
from typing import Optional

class UserRepository(BaseMongoRepository[User]):
    """
    Repository for User objects.

    Handles creation, indexing, and retrieval of user profiles.
    """
    def __init__(self):
        """Initializes the User repository."""
        # Link the collection name with the model type
        super().__init__("users", User)

    async def setup_indexes(self):
        """
        Configures MongoDB indexes for the users collection.

        Creates a unique index on 'username'.
        """
        # Configures Mongo so that "name" is a unique value
        indice_email = IndexModel([("username", ASCENDING)], unique=True)
        await self.collection.create_indexes([indice_email])

    async def find_by_name(self, name: str) -> Optional[User]:
        """
        Search for a user by their username.

        Args:
            name (str): The unique username.

        Returns:
            Optional[User]: The user instance if found, None otherwise.
        """
        return await self.find_one({"username": name})
