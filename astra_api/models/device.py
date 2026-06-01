"""
ASTRA - Automated Smart Telescope Remote Assistant
Copyright (C) 2026 Jesus Basallote

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
Models for representing Edge devices in astra_api.
"""
from datetime import datetime, timezone
import random
import string

from pydantic import BaseModel, Field
from typing import Literal

def generate_name():
    """
    Generates a random human-readable name for a device.

    Returns:
        str: A generated name like 'dev-a1b2c3d4e5'.
    """
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"dev-{suffix}"

class DeviceAccess(BaseModel):
    """
    Model representing user access permissions for a device.

    Attributes:
        user_id (str): The ID of the user.
        role (Literal["owner", "guest"]): The user's role for this device.
    """
    user_id: str
    role: Literal["owner", "guest"]

class Device(BaseModel):
    """
    Model representing an Edge device (telescope controller).

    Attributes:
        device_id (str): The unique hardware identifier of the device.
        device_token (str): The authentication token for the device.
        name (str): The human-readable name of the device.
        owner (str): The username of the device owner.
        linked (datetime): The timestamp when the device was first linked.
        access_list (list[DeviceAccess]): List of users with access to this device.
    """
    device_id: str
    device_token: str
    name: str = Field(default_factory=generate_name)
    owner: str
    linked: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    access_list: list[DeviceAccess] = Field(default_factory=list)
