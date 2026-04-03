from models.user import Location, User
from repositories.user import UserRepository
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
    
    async def add_location(self, username: str, location: Location) -> bool:
        
        update_data = {"$push": {"locations": location.model_dump()}}
        return await self.repo.update_one({"username": username}, update_data)

    async def remove_location(self, username: str, location_id: str) -> bool:
        
        update_data = {"$pull": {"locations": {"id": location_id}}}
        return await self.repo.update_one({"username": username}, update_data)
        
