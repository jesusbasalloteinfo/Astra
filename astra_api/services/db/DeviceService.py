"""
Service for managing Edge device business logic in astra_api.
"""
import secrets
import hashlib
from typing import List
from models.device import Device, DeviceAccess
from repositories.device import DeviceRepository
from core.db_exceptions import ObjectNotFoundError, ObjectAlreadyExistsError

def hash_token(plain_token: str) -> str:
    """
    Applies SHA-256 hashing to a plain text token.

    Args:
        plain_token (str): The raw token string.

    Returns:
        str: The hex digest of the hashed token.
    """
    return hashlib.sha256(plain_token.encode('utf-8')).hexdigest()

class DeviceService:
    """
    Service to manage device registration, access control, and authentication.
    """
    def __init__(self):
        """Initializes the Device service."""
        self.repo = DeviceRepository()

    async def get_device(self, device_id: str) -> Device:
        """
        Retrieves a device by its ID.

        Args:
            device_id (str): The device hardware ID.

        Returns:
            Device: The device instance.

        Raises:
            ObjectNotFoundError: If the device does not exist.
        """
        device = await self.repo.find_by_device_id(device_id)
        if not device:
            raise ObjectNotFoundError(f"Device {device_id} not found")
        return device

    async def get_user_device(self, device_id: str, requesting_user_id: str) -> Device:
        """
        Retrieves a device, ensuring the requester has permission to see it.

        Args:
            device_id (str): The device hardware ID.
            requesting_user_id (str): The ID of the user requesting access.

        Returns:
            Device: The device instance.

        Raises:
            ObjectNotFoundError: If the device doesn't exist or access is denied.
        """
        device = await self.get_device(device_id)
        
        has_access = any(access.user_id == requesting_user_id for access in device.access_list)
        
        if not has_access:
            raise ObjectNotFoundError(f"Device {device_id} not found")
            
        return device
    
    async def get_user_devices(self, user_id: str) -> List[Device]:
        """
        Retrieves all devices that a specific user has access to.

        Args:
            user_id (str): The user ID.

        Returns:
            List[Device]: A list of devices.
        """
        return await self.repo.find_by_user_id(user_id)
    
    async def update_device_info(self, device_id: str, requesting_user_id: str, **update_data) -> bool:
        """
        Updates device information fields.

        Only the owner of the device can update its information.

        Args:
            device_id (str): The device hardware ID.
            requesting_user_id (str): The ID of the user requesting the update.
            **update_data: The fields to update.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            ObjectNotFoundError: If the device is not found or the user is not the owner.
        """
        device = await self.get_user_device(device_id, requesting_user_id)
        
        if device.owner != requesting_user_id:
            raise ObjectNotFoundError(f"Device {device_id} not found")

        # Clear null data
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if not update_data:
            return False

        return await self.repo.update_one(
            {"device_id": device_id},
            {"$set": update_data}
        )

    async def link_device(self, device_id: str, user_id: str) -> str:
        """
        Pairs a new device with a user and generates an access token.

        Args:
            device_id (str): The device hardware ID.
            user_id (str): The ID of the user who will own the device.

        Returns:
            str: The plain text access token generated for the device.

        Raises:
            ObjectAlreadyExistsError: If the device is already paired.
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
        """
        Validates if the provided plain token matches the stored hash for a device.

        Args:
            device_id (str): The device hardware ID.
            plain_token (str): The token provided by the device.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        try:
            device = await self.get_device(device_id)
            received_hash = hash_token(plain_token)
            return device.device_token == received_hash
        except ObjectNotFoundError:
            return False

    async def share_device(self, device_id: str, target_user_id: str, role: str = "guest") -> bool:
        """
        Grants a new user access to an existing device.

        Args:
            device_id (str): The device hardware ID.
            target_user_id (str): The ID of the user to share access with.
            role (str): The role to assign (must be 'guest').

        Returns:
            bool: True if access was granted successfully.

        Raises:
            ValueError: If an attempt is made to assign 'owner' role.
            ObjectAlreadyExistsError: If the user already has access.
        """
        if role == "owner":
            raise ValueError("Only one owner allowed")
        
        device = await self.get_device(device_id)
        
        if any(access.user_id == target_user_id for access in device.access_list):
            raise ObjectAlreadyExistsError(f"User {target_user_id} already has access to {device_id}")

        new_access = DeviceAccess(user_id=target_user_id, role=role)
        return await self.repo.add_user_access(device_id, new_access)

    async def revoke_access(self, device_id: str, target_user_id: str) -> bool:
        """
        Revokes a guest user's access to a device.

        Args:
            device_id (str): The device hardware ID.
            target_user_id (str): The ID of the user whose access is being revoked.

        Returns:
            bool: True if access was revoked.

        Raises:
            ValueError: If an attempt is made to revoke the owner's access.
            ObjectNotFoundError: If the user did not have access to the device.
        """
        device = await self.get_device(device_id)

        if device.owner == target_user_id:
            raise ValueError("Unable to remove owner")
        
        access_entry = next((a for a in device.access_list if a.user_id == target_user_id), None)
        if not access_entry:
            raise ObjectNotFoundError(f"User {target_user_id} does not have access to {device_id}")

        return await self.repo.remove_user_access(device_id, target_user_id)
    
    async def unlink_device(self, device_id: str, requesting_user_id: str) -> bool:
        """
        Deletes a device registration.

        Args:
            device_id (str): The device hardware ID.
            requesting_user_id (str): The ID of the user (must be the owner).

        Returns:
            bool: True if the device was deleted.

        Raises:
            ObjectNotFoundError: If the device is not found or the user is not the owner.
        """
        device = await self.get_device(device_id)
                
        if device.owner != requesting_user_id:
            raise ObjectNotFoundError(f"Device {device_id} not found")

        return await self.repo.delete_one({"device_id": device_id})
