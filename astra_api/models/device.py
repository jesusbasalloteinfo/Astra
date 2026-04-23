from datetime import datetime, timezone
import random
import string

from pydantic import BaseModel, Field
from typing import Literal

def generate_name():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"dev-{suffix}"

class DeviceAccess(BaseModel):
    user_id: str
    role: Literal["owner", "guest"]

class Device(BaseModel):
    device_id: str
    device_token: str
    name: str = Field(default_factory=generate_name)
    owner: str
    linked: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    access_list: list[DeviceAccess] = Field(default_factory=list)