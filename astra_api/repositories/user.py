from models.user import User
from repositories.base import BaseMongoRepository
from typing import Optional

class UserRepository(BaseMongoRepository[User]):
    def __init__(self):
        # Link the collection name with the model type
        super().__init__("users", User)

    async def find_by_name(self, name: str) -> Optional[User]:
        return await self.find_one({"name": name})