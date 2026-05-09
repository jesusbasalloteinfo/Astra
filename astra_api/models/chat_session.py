from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

from services.assistant.models import ChatMessage

class ChatSession(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    observation_id: str
    title: str = "Default Chat"
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {"populate_by_name": True}
