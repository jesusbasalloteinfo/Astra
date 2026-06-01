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
Models for the AI assistant chat, tool calls, and streaming events in astra_api.
"""
from typing import List, Optional, Any, Dict, Literal
from pydantic import BaseModel, Field

# --- Chat State Models ---

class ToolCallDefinition(BaseModel):
    """Represents the definition of a function tool call."""
    name: str
    arguments: str

class ToolCall(BaseModel):
    """
    Represents a specific tool call instance in a chat message.

    Attributes:
        id (str): Unique identifier for the tool call.
        type (Literal["function"]): Type of tool call.
        function (ToolCallDefinition): The function details.
    """
    id: str
    type: Literal["function"] = "function"
    function: ToolCallDefinition

class ToolCallBuilder(BaseModel):
    """
    Helper model for incrementally building a tool call from stream chunks.
    """
    id: str = ""
    name: str = ""
    arguments: str = ""

class BaseToolResponse(BaseModel):
    """
    Standardized response from a tool execution.

    Attributes:
        status (Literal["success", "error"]): Outcome status.
        message (Optional[str]): Descriptive message about the outcome.
        data (Optional[Any]): Structured data returned by the tool.
        frontend_action (Optional[bool]): Flag indicating if the UI should perform an action.
    """
    status: Literal["success", "error"] = "success"
    message: Optional[str] = None
    data: Optional[Any] = None
    frontend_action: Optional[bool] = False

class ToolResult(BaseModel):
    """
    Consolidated result of a tool execution for internal processing.

    Attributes:
        tc_id (str): The tool call ID.
        tool_name (str): The name of the tool executed.
        result (BaseToolResponse): The execution response.
        arguments (Any): The arguments used for execution.
    """
    tc_id: str
    tool_name: str
    result: BaseToolResponse
    arguments: Any = None

class ChatMessage(BaseModel):
    """
    Model representing a single message in a chat history.

    Attributes:
        role (Literal["system", "user", "assistant", "tool"]): The sender's role.
        name (Optional[str]): Optional name for the sender (e.g., tool name).
        tool_call_id (Optional[str]): ID of the tool call this message responds to.
        reasoning_content (Optional[str]): Internal thought process of the model.
        content (Optional[str]): The message text content.
        tool_calls (Optional[List[ToolCall]]): List of tool calls initiated in this message.
    """
    role: Literal["system", "user", "assistant", "tool"]
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    reasoning_content: Optional[str] = None
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

class ChatHistory(BaseModel):
    """
    Wrapper for a sequence of chat messages.
    """
    messages: List[ChatMessage] = Field(default_factory=list)

    def add_message(self, message: ChatMessage):
        """Adds a message to the history."""
        self.messages.append(message)

# --- SSE Event Models ---

class SSEEvent(BaseModel):
    """Base class for Server-Sent Events (SSE) emitted by the assistant."""
    event_type: str

class TextEvent(SSEEvent):
    """Emitted when a text chunk is generated."""
    event_type: Literal["text"] = "text"
    text: str

class ReasoningEvent(SSEEvent):
    """Emitted when a reasoning chunk is generated."""
    event_type: Literal["reasoning"] = "reasoning"
    text: str

class ToolCallStartEvent(SSEEvent):
    """Emitted when the assistant starts a tool call."""
    event_type: Literal["tool_call_start"] = "tool_call_start"
    tool_name: str
    tool_call_id: str

class ToolCallChunkEvent(SSEEvent):
    """Emitted for each chunk of tool arguments."""
    event_type: Literal["tool_call_chunk"] = "tool_call_chunk"
    chunk: str

class ToolExecutionEvent(SSEEvent):
    """Emitted when a tool execution completes."""
    event_type: Literal["tool_execution"] = "tool_execution"
    tool_call_id: str
    tool_name: str
    arguments: Any = None
    result: BaseToolResponse

class ErrorEvent(SSEEvent):
    """Emitted when an error occurs during processing."""
    event_type: Literal["error"] = "error"
    message: str
    details: Optional[str] = None

class FinalEvent(SSEEvent):
    """Emitted when the generation process finishes."""
    event_type: Literal["finish"] = "finish"
