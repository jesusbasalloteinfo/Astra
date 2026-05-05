from typing import List, Optional, Any, Dict, Literal
from pydantic import BaseModel, Field

# --- Chat State Models ---

class ToolCallDefinition(BaseModel):
    name: str
    arguments: str

class ToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: ToolCallDefinition

class ToolCallBuilder(BaseModel):
    id: str = ""
    name: str = ""
    arguments: str = ""

class BaseToolResponse(BaseModel):
    status: Literal["success", "error"] = "success"
    message: Optional[str] = None
    data: Optional[Any] = None
    frontend_action: Optional[bool] = False

class ToolResult(BaseModel):
    tc_id: str
    tool_name: str
    result: BaseToolResponse
    arguments: Any = None

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    reasoning_content: Optional[str] = None
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

class ChatHistory(BaseModel):
    messages: List[ChatMessage] = Field(default_factory=list)

    def add_message(self, message: ChatMessage):
        self.messages.append(message)

# --- SSE Event Models ---

class SSEEvent(BaseModel):
    event_type: str

class TextEvent(SSEEvent):
    event_type: Literal["text"] = "text"
    text: str

class ReasoningEvent(SSEEvent):
    event_type: Literal["reasoning"] = "reasoning"
    text: str

class ToolCallStartEvent(SSEEvent):
    event_type: Literal["tool_call_start"] = "tool_call_start"
    tool_name: str
    tool_call_id: str

class ToolCallChunkEvent(SSEEvent):
    event_type: Literal["tool_call_chunk"] = "tool_call_chunk"
    chunk: str

class ToolExecutionEvent(SSEEvent):
    event_type: Literal["tool_execution"] = "tool_execution"
    tool_name: str
    arguments: Any = None
    result: BaseToolResponse

class ErrorEvent(SSEEvent):
    event_type: Literal["error"] = "error"
    message: str
    details: Optional[str] = None

class FinalEvent(SSEEvent):
    event_type: Literal["finish"] = "finish"