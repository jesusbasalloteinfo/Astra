from models.auth import AuthUser
from repositories.base import BaseMongoRepository
from typing import Optional
from pymongo import IndexModel, ASCENDING

class AuthRepository(BaseMongoRepository[AuthUser]):
    def __init__(self):
        super().__init__("users", AuthUser)

    async def setup_indexes(self):
        """Configure unique indexes for username and email."""
        idx_username = IndexModel([("username", ASCENDING)], unique=True)
        idx_email = IndexModel([("email", ASCENDING)], unique=True)
        await self.collection.create_indexes([idx_username, idx_email])

    async def find_by_username(self, username: str) -> Optional[AuthUser]:
        return await self.find_one({"username": username})

    async def find_by_email(self, email: str) -> Optional[AuthUser]:
        return await self.find_one({"email": email})
