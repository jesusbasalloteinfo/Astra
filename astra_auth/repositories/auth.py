from models.auth import AuthUser
from repositories.base import BaseMongoRepository
from typing import Optional
from pymongo import IndexModel, ASCENDING

class AuthRepository(BaseMongoRepository[AuthUser]):
    """Repository for managing authentication user data in MongoDB."""

    def __init__(self):
        """Initialize the AuthRepository with the 'users' collection."""
        super().__init__("users", AuthUser)

    async def setup_indexes(self):
        """Configure unique indexes for username and email in the users collection."""
        idx_username = IndexModel([("username", ASCENDING)], unique=True)
        idx_email = IndexModel([("email", ASCENDING)], unique=True)
        await self.collection.create_indexes([idx_username, idx_email])

    async def find_by_username(self, username: str) -> Optional[AuthUser]:
        """Find a user by their username.

        Args:
            username (str): The username to search for.

        Returns:
            Optional[AuthUser]: The user object if found, otherwise None.
        """
        return await self.find_one({"username": username})

    async def find_by_email(self, email: str) -> Optional[AuthUser]:
        """Find a user by their email address.

        Args:
            email (str): The email to search for.

        Returns:
            Optional[AuthUser]: The user object if found, otherwise None.
        """
        return await self.find_one({"email": email})
