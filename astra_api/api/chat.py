import json
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.assistant import FinalEvent
from core.dependencies import get_request_user
from services.assistant import stream_chat, ChatHistory, ChatMessage
from services.assistant.examples import create_get_user_profile_tool, create_weather_tool

router = APIRouter()

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gemini-3.1-flash" # default model, could be overridden

async def sse_event_generator(history: ChatHistory, tools: list, model: str):
    """
    Consumes the internal stream_chat generator and formats the 
    internal SSEEvent objects into Server-Sent Events text chunks.
    """
    async for event in stream_chat(history=history, tools=tools, model=model):
        # Dump the event as JSON
        event_data = event.model_dump_json(exclude_none=True)
        # Format as standard SSE
        yield f"data: {event_data}\n\n"
        
    
    yield f"data: {FinalEvent().model_dump_json()}\n\n"

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Endpoint for streaming LLM chat.
    Accepts a history of messages and streams back the assistant's response
    and any tool execution events using Server-Sent Events (SSE).
    """
    
    # Initialize the history
    history = ChatHistory(messages=request.messages)
    
    if not history.messages or history.messages[0].role != "system":
        history.messages.insert(0, ChatMessage(
            role="system",
            content="You are Astra, an intelligent and helpful assistant for the Astra system. You have access to various tools."
        ))

    # Initialize tools
    tools = [
        create_get_user_profile_tool(user_id="aaaa", db_connection="dummy-db"),
        create_weather_tool(location="Test, Testilandia"),
    ]

    # Return a StreamingResponse
    return StreamingResponse(
        sse_event_generator(history, tools, request.model),
        media_type="text/event-stream"
    )
