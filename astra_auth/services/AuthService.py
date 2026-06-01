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

import bcrypt
from typing import Optional
from models.auth import AuthUser, UserRegister, UserLogin, UserProfile
from repositories.auth import AuthRepository
from core.logging_utils import get_logger

class AuthService:
    """Service for handling user authentication and profile management."""

    def __init__(self):
        """Initialize the AuthService with an AuthRepository and a logger."""
        self.repo = AuthRepository()
        self.logger = get_logger("AuthService")

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password (str): The plain-text password to hash.

        Returns:
            str: The hashed password.
        """
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8')

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash.

        Args:
            plain_password (str): The plain-text password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the password is valid, False otherwise.
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    async def register(self, data: UserRegister) -> bool:
        """Register a new user.

        Args:
            data (UserRegister): The registration data containing username, email, and password.

        Returns:
            bool: True if registration is successful, False if the username or email already exists.
        """
        # Check if user already exists
        if await self.repo.find_by_username(data.username):
            return False
        if await self.repo.find_by_email(data.email):
            return False

        hashed_password = self._hash_password(data.password)
        new_user = AuthUser(
            username=data.username,
            email=data.email,
            password=hashed_password
        )
        
        await self.repo.insert_one(new_user)
        return True

    async def authenticate(self, data: UserLogin) -> Optional[AuthUser]:
        """Verify user credentials and return user object if successful.

        Args:
            data (UserLogin): The login credentials (username and password).

        Returns:
            Optional[AuthUser]: The user object if authentication succeeds, otherwise None.
        """
        user = await self.repo.find_by_username(data.username)
        if not user or not self._verify_password(data.password, user.password):
            return None
        return user

    async def get_profile(self, username: str) -> Optional[UserProfile]:
        """Get user profile information.

        Args:
            username (str): The username of the profile to retrieve.

        Returns:
            Optional[UserProfile]: The user profile if found, otherwise None.
        """
        user = await self.repo.find_by_username(username)
        if user:
            return UserProfile(
                username=user.username,
                email=user.email,
                profile_picture_url=user.profile_picture_url,
                creation=user.creation
            )
        return None

    async def update_profile_picture(self, username: str, url: str) -> bool:
        """Update the user's profile picture URL.

        Args:
            username (str): The username of the user whose picture is being updated.
            url (str): The new profile picture URL.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        return await self.repo.update_one(
            {"username": username},
            {"$set": {"profile_picture_url": url}}
        )
