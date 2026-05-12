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
    
    async def update_user(self, username: str, data: dict) -> bool:
        """Update user profile details."""
        return await self.repo.update_one({"username": username}, {"$set": data})

    async def add_location(self, username: str, location: Location) -> bool:

        if location.is_default:
            await self.repo.update_one(
                {"username": username},
                {"$set": {"locations.$[].is_default": False}}
            )
        
        # First location
        user = await self.get_user(username)
        if not user.locations:
            location.is_default = True

        update_data = {"$push": {"locations": location.model_dump()}}
        return await self.repo.update_one({"username": username}, update_data)

    async def remove_location(self, username: str, location_id: str) -> bool:

        user = await self.get_user(username)
        loc_to_remove = next((l for l in user.locations if l.id == location_id), None)
        
        if not loc_to_remove:
            return False

        # Delete the location
        delete_result = await self.repo.update_one(
            {"username": username},
            {"$pull": {"locations": {"id": location_id}}}
        )

        # Promote the first if default deleted
        if loc_to_remove.is_default:
            remaining_locs = [l for l in user.locations if l.id != location_id]
            if remaining_locs:
                new_default_id = remaining_locs[0].id
                await self.repo.update_one(
                    {"username": username, "locations.id": new_default_id},
                    {"$set": {"locations.$.is_default": True}}
                )

        return delete_result
