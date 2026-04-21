import secrets
import hashlib
from typing import List
from models.device import Device, DeviceAccess
from repositories.device import DeviceRepository
from core.db_exceptions import ObjectNotFoundError, ObjectAlreadyExistsError

def hash_token(plain_token: str) -> str:
    """Apply a SHA-256 to a plain token"""
    return hashlib.sha256(plain_token.encode('utf-8')).hexdigest()

class DeviceService:
    def __init__(self):
        self.repo = DeviceRepository()

    async def get_device(self, device_id: str) -> Device:
        """Get a device by id"""
        device = await self.repo.find_by_device_id(device_id)
        if not device:
            raise ObjectNotFoundError(f"Device {device_id} not found")
        return device

    async def get_user_device(self, device_id: str, requesting_user_id: str) -> Device:
        """Get a device ensuring the requester has permissions to see it"""
        device = await self.get_device(device_id)
        
        has_access = any(access.user_id == requesting_user_id for access in device.access_list)
        
        if not has_access:
            raise ObjectNotFoundError(f"Device {device_id} not found")
            
        return device
    
    async def get_user_devices(self, user_id: str) -> List[Device]:
        """Get all user allowed devices"""
        return await self.repo.find_by_user_id(user_id)

    async def link_device(self, device_id: str, user_id: str) -> str:
        """
        Pairs a device with a user
        """
        # Generate a token
        plain_token = secrets.token_urlsafe(32)
        hashed_token = hash_token(plain_token)

        existing_device = await self.repo.find_by_device_id(device_id)

        if existing_device:
            raise ObjectAlreadyExistsError("Device already paired!") 
        else:
            # New device
            new_device = Device(
                device_id=device_id,
                device_token=hashed_token,
                owner= user_id,
                access_list=[DeviceAccess(user_id=user_id, role="owner")]
            )
            await self.repo.insert_one(new_device)

        return plain_token

    async def validate_tunnel_token(self, device_id: str, plain_token: str) -> bool:
        """Checks if the device token is correct"""
        try:
            device = await self.get_device(device_id)
            received_hash = hash_token(plain_token)
            return device.device_token == received_hash
        except ObjectNotFoundError:
            return False

    async def share_device(self, device_id: str, target_user_id: str, role: str = "guest") -> bool:
        """Share the device with another user"""
        if role == "owner":
            raise ValueError("Only one owner allowed")
        
        device = await self.get_device(device_id)
        
        if any(access.user_id == target_user_id for access in device.access_list):
            raise ObjectAlreadyExistsError(f"User {target_user_id} already has access to {device_id}")

        new_access = DeviceAccess(user_id=target_user_id, role=role)
        return await self.repo.add_user_access(device_id, new_access)

    async def revoke_access(self, device_id: str, target_user_id: str) -> bool:
        """Remove access to a device for a gest user"""
        device = await self.get_device(device_id)

        if device.owner == target_user_id:
            raise ValueError("Unable to remove owner")
        
        access_entry = next((a for a in device.access_list if a.user_id == target_user_id), None)
        if not access_entry:
            raise ObjectNotFoundError(f"User {target_user_id} does not have access to {device_id}")

        return await self.repo.remove_user_access(device_id, target_user_id)
    
    async def unlink_device(self, device_id: str, requesting_user_id: str) -> bool:
        """
        Deletes a device
        """
        device = await self.get_device(device_id)
                
        if device.owner != requesting_user_id:
            raise PermissionError("Only owner can delete the device")

        return await self.repo.delete_one({"device_id": device_id})