from models.user import User
from repositories.user import UserRepository
from fastapi import HTTPException

class UserService:
    def __init__(self):
        self.repo = UserRepository()

    async def create_user(self, data: User) -> str:

        exists = await self.repo.find_by_name(data.username)
        if exists:
            raise HTTPException(status_code=400, detail="The name is already taken")
        
        return await self.repo.insert_one(data)

    async def get_user(self, name: str) -> User:
        user = await self.repo.find_by_name(name)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user