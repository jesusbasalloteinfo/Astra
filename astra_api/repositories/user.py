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
