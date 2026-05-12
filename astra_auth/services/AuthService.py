import bcrypt
from typing import Optional
from models.auth import AuthUser, UserRegister, UserLogin, UserProfile
from repositories.auth import AuthRepository
from core.logging_utils import get_logger

class AuthService:
    def __init__(self):
        self.repo = AuthRepository()
        self.logger = get_logger("AuthService")

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8')

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    async def register(self, data: UserRegister) -> bool:
        """Register a new user."""
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
        """Verify user credentials and return user object if successful."""
        user = await self.repo.find_by_username(data.username)
        if not user or not self._verify_password(data.password, user.password):
            return None
        return user

    async def get_profile(self, username: str) -> Optional[UserProfile]:
        """Get user profile information."""
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
        """Update the user's profile picture URL."""
        return await self.repo.update_one(
            {"username": username},
            {"$set": {"profile_picture_url": url}}
        )
