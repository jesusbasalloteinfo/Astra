"""
Repository for managing Edge device data in MongoDB.
"""
from typing import List, Optional
from pymongo import IndexModel, ASCENDING

from models.device import Device, DeviceAccess
from repositories.base import BaseMongoRepository


class DeviceRepository(BaseMongoRepository[Device]):
    """
    Repository for Device objects.

    Handles registration, access control, and token management for Edge devices.
    """
    def __init__(self):
        """Initializes the Device repository."""
        super().__init__(collection_name="devices", model_class=Device)

    async def setup_indexes(self):
        """
        Fast search indexes and device ID identification.

        Creates a unique index on 'device_id' and a nested index on 'access_list.user_id'.
        """
        indexes = [
            IndexModel([("device_id", ASCENDING)], unique=True),

            # Nested index to search users faster
            IndexModel([("access_list.user_id", ASCENDING)])
        ]
        await self.collection.create_indexes(indexes)


    async def find_by_device_id(self, device_id: str) -> Optional[Device]:
        """
        Search for a device by its hardware serial ID.

        Args:
            device_id (str): The device hardware ID.

        Returns:
            Optional[Device]: The device instance if found, None otherwise.
        """
        return await self.find_one({"device_id": device_id})

    async def find_by_user_id(self, user_id: str) -> List[Device]:
        """
        Search for all devices that a user has access to.

        Args:
            user_id (str): The username or ID of the user.

        Returns:
            List[Device]: A list of devices.
        """
        return await self.find_many({"access_list.user_id": user_id})


    async def add_user_access(self, device_id: str, access: DeviceAccess) -> bool:
        """
        Grant a user access to a device.

        Args:
            device_id (str): The device hardware ID.
            access (DeviceAccess): The access details (user_id and role).

        Returns:
            bool: True if the access list was updated, False otherwise.
        """
        return await self.update_one(
            query={"device_id": device_id},
            update_data={"$push": {"access_list": access.model_dump()}}
        )

    async def remove_user_access(self, device_id: str, user_id: str) -> bool:
        """
        Revoke a user's access to a device.

        Args:
            device_id (str): The device hardware ID.
            user_id (str): The ID of the user to remove.

        Returns:
            bool: True if the user was removed from the access list, False otherwise.
        """
        return await self.update_one(
            query={"device_id": device_id},
            update_data={"$pull": {"access_list": {"user_id": user_id}}}
        )

    async def update_token(self, device_id: str, new_token: str) -> bool:
        """
        Update the secret authentication token for a device.

        Args:
            device_id (str): The device hardware ID.
            new_token (str): The new authentication token.

        Returns:
            bool: True if the token was updated, False otherwise.
        """
        return await self.update_one(
            query={"device_id": device_id},
            update_data={"$set": {"device_token": new_token}}
        )
