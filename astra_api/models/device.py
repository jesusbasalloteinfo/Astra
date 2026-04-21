import random
import string

from pydantic import BaseModel, Field
from typing import Literal

def generate_name():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"Dev-{suffix}"

class DeviceAccess(BaseModel):
    user_id: str
    role: Literal["owner", "guest"]

class Device(BaseModel):
    device_id: str
    device_token: str
    name: str = Field(default_factory=generate_name)
    owner: str

    access_list: list[DeviceAccess] = Field(default_factory=list)