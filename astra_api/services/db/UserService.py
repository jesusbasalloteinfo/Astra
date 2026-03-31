from models.user import User
from repositories.user import UserRepository
from fastapi import HTTPException
from core.db_exceptions import ObjectAlreadyExistsError, ObjectNotFoundError

class UserService:
    def __init__(self):
        self.repo = UserRepository()

    async def create_user(self, data: User) -> str:

        exists = await self.repo.find_by_name(data.username)
        if exists:
            raise ObjectAlreadyExistsError(f"User {data.username} already exists")
        
        return await self.repo.insert_one(data)

    async def get_user(self, username: str) -> User:
        user = await self.repo.find_by_name(username)
        if not user:
            raise ObjectNotFoundError(f"User {username} not found")
        return user

    async def ensure_user(self, username: str) -> str:

        user=User(username=username)

        try:
            return await self.create_user(user)
        except ObjectAlreadyExistsError:
            return username
        
