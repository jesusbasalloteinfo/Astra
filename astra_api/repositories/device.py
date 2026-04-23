from typing import List, Optional
from pymongo import IndexModel, ASCENDING

from models.device import Device, DeviceAccess
from repositories.base import BaseMongoRepository


class DeviceRepository(BaseMongoRepository[Device]):
    def __init__(self):
        super().__init__(collection_name="devices", model_class=Device)

    async def setup_indexes(self):
        """Fast search indexs and device id identification"""
        indexes = [
            IndexModel([("device_id", ASCENDING)], unique=True),

            # Nested index to search users faster
            IndexModel([("access_list.user_id", ASCENDING)])
        ]
        await self.collection.create_indexes(indexes)


    async def find_by_device_id(self, device_id: str) -> Optional[Device]:
        """Search by device serial id"""
        return await self.find_one({"device_id": device_id})

    async def find_by_user_id(self, user_id: str) -> List[Device]:
        """Search by user allowed devices"""
        return await self.find_many({"access_list.user_id": user_id})


    async def add_user_access(self, device_id: str, access: DeviceAccess) -> bool:
        """Share a device with a user"""
        return await self.update_one(
            query={"device_id": device_id},
            update_data={"$push": {"access_list": access.model_dump()}}
        )

    async def remove_user_access(self, device_id: str, user_id: str) -> bool:
        """Remove the user from the device"""
        return await self.update_one(
            query={"device_id": device_id},
            update_data={"$pull": {"access_list": {"user_id": user_id}}}
        )

    async def update_token(self, device_id: str, new_token: str) -> bool:
        """Update secret token"""
        return await self.update_one(
            query={"device_id": device_id},
            update_data={"$set": {"device_token": new_token}}
        )
