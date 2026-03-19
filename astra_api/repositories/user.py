from models.user import User
from repositories.base import *
from typing import Optional

class UserRepository(BaseMongoRepository[User]):
    def __init__(self):
        # Link the collection name with the model type
        super().__init__("users", User)

    async def setup_indexes(self):

        # Configures Mongo so that "name" is a unique value
        indice_email = IndexModel([("username", ASCENDING)], unique=True)
        await self.collection.create_indexes([indice_email])

    async def find_by_name(self, name: str) -> Optional[User]:
        return await self.find_one({"username": name})