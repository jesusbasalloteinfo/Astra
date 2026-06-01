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
