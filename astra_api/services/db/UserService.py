"""
Service for managing user profiles and settings business logic in astra_api.
"""
from models.user import Location, User
from repositories.user import UserRepository
from core.db_exceptions import ObjectAlreadyExistsError, ObjectNotFoundError

class UserService:
    """
    Service to coordinate user profile management and location synchronization.
    """
    def __init__(self):
        """Initializes the User service."""
        self.repo = UserRepository()

    async def create_user(self, data: User) -> str:
        """
        Creates a new user profile in the database.

        Args:
            data (User): The user data model.

        Returns:
            str: The identifier of the created user.

        Raises:
            ObjectAlreadyExistsError: If a user with the same username exists.
        """
        exists = await self.repo.find_by_name(data.username)
        if exists:
            raise ObjectAlreadyExistsError(f"User {data.username} already exists")
        
        return await self.repo.insert_one(data)

    async def get_user(self, username: str) -> User:
        """
        Retrieves a user profile by username.

        Args:
            username (str): The unique username.

        Returns:
            User: The user profile instance.

        Raises:
            ObjectNotFoundError: If the user is not found.
        """
        user = await self.repo.find_by_name(username)
        if not user:
            raise ObjectNotFoundError(f"User {username} not found")
        return user

    async def ensure_user(self, username: str) -> str:
        """
        Ensures that a user profile exists, creating it if necessary.

        This is typically used during authentication sync.

        Args:
            username (str): The username to ensure.

        Returns:
            str: The username.
        """
        user = User(username=username)

        try:
            return await self.create_user(user)
        except ObjectAlreadyExistsError:
            return username
    
    async def update_user(self, username: str, data: dict) -> bool:
        """
        Update user profile details.

        Args:
            username (str): The unique username.
            data (dict): The fields and values to update.

        Returns:
            bool: True if the update was successful.
        """
        return await self.repo.update_one({"username": username}, {"$set": data})

    async def add_location(self, username: str, location: Location) -> bool:
        """
        Adds a new geographic location to a user's profile.

        If the location is marked as default, other locations are updated.
        The first location added to a user is automatically marked as default.

        Args:
            username (str): The unique username.
            location (Location): The location data model.

        Returns:
            bool: True if the location was added.
        """
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
        """
        Removes a location from a user's profile.

        If the removed location was the default, another location is promoted.

        Args:
            username (str): The unique username.
            location_id (str): The unique identifier of the location to remove.

        Returns:
            bool: True if the location was removed.
        """
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
