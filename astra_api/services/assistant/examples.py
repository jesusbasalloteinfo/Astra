import asyncio
from functools import partial
from pydantic import BaseModel, Field
from .tools import CurriedTool

async def backend_get_user_profile(user_id: str, db_connection: str, include_email: bool = False):
    print(f"\n[Backend Log] Async accessing DB: {db_connection} for User ID: {user_id}")
    await asyncio.sleep(1.5) # Simulate network delay
    profile = {
        "name": "James Bond",
        "role": "Admin",
        "work": "MI6, London",
        "preferences": {"gun": True, "cool_car": True}
    }
    if include_email:
        profile["email"] = "james@jamesbond.007"
    return profile

def backend_get_weather(location: str):
    print(f"\n[Backend Log] Async fetching weather using implicit location: {location}")
    return {"weather": "Sunny", "temperature_celsius": 25, "location": location}

# --- 2. Pydantic Models for the LLM Arguments ---

class UserProfileArgs(BaseModel):
    include_email: bool = Field(False, description="Whether to include the user's email address in the response.")

class EmptyArgs(BaseModel):
    pass

class MoveElementArgs(BaseModel):
    x: int = Field(..., description="The X coordinate to move the element to.")
    y: int = Field(..., description="The Y coordinate to move the element to.")

# --- 3. Tool Creation Factories (Partial Application) ---

def create_get_user_profile_tool(user_id: str, db_connection: str) -> CurriedTool:
    return CurriedTool(
        name="get_user_profile",
        description="Retrieves the current user's profile information.",
        args_model=UserProfileArgs,
        func=partial(backend_get_user_profile, user_id=user_id, db_connection=db_connection)
    )

def create_weather_tool(location: str) -> CurriedTool:
    return CurriedTool(
        name="get_weather",
        description="Retrieves the current weather for the user. No arguments are needed as the system already knows the user's location.",
        args_model=EmptyArgs,
        func=partial(backend_get_weather, location=location)
    )

def create_move_element_tool() -> CurriedTool:
    return CurriedTool(
        name="move_element",
        description="Moves a UI element to specific X and Y coordinates on the user's screen.",
        args_model=MoveElementArgs,
        frontend_only=True
    )