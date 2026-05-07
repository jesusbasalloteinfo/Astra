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
from services.tools.observation import fly_to_const_tool, select_object_element_tool
from services.tools import (
    WikiEngine,
    create_search_article_tool,
    create_get_article_intro_tool,
    create_get_article_section_tool,
    create_get_article_infotable_tool
)

from services.db.ChatSessionService import ChatSessionService

router = APIRouter()
wiki_instance=WikiEngine(lang="en")

class StreamRequest(BaseModel):
    message: Optional[ChatMessage] = None
    model: str = "astra_ai"

chat_service = ChatSessionService()

SYSTEM_PROMPT = "You are Astra, an intelligent and helpful assistant for the Astra system. You have access to various tools. ALWAYS tell the user what are you going to do BEFORE any toolcall that you want to call."

@router.get("/session/{observation_id}")
async def get_chat_session(observation_id: str, username: str = Depends(get_request_user)):
    """
    Retrieves the active chat session for a given observation, 
    creating it if it doesn't exist.
    """
    session = await chat_service.get_or_create_session(observation_id, username)
    return session

async def sse_event_generator(history: ChatHistory, tools: list, model: str, session_id: str, system_prompt: str):
    """
    Consumes the internal stream_chat generator and formats the 
    internal SSEEvent objects into Server-Sent Events text chunks.
    """
    try:
        async for event in stream_chat(history=history, tools=tools, model=model, system_prompt=system_prompt):
            # Dump the event as JSON
            event_data = event.model_dump_json(exclude_none=True)
            # Format as standard SSE
            yield f"data: {event_data}\n\n"
            
        yield f"data: {FinalEvent().model_dump_json()}\n\n"
        
        # Save normally when stream finishes
        await chat_service.save_messages(session_id, history.messages)
        
    except asyncio.CancelledError:
        # If the user aborts the request, we still want to save the partial history.
        #  We use create_task to spawn a fire-and-forget task that won't be killed 
        asyncio.create_task(chat_service.save_messages(session_id, history.messages))
        raise

@router.post("/stream/{session_id}")
async def chat_stream(session_id: str, request: StreamRequest, username: str = Depends(get_request_user)):
    """
    Endpoint for streaming LLM chat.
    Accepts a session ID and a new message, appending it to the history 
    and streaming back the assistant's response.
    """
    
    # 1. Fetch the existing session
    session = await chat_service.get_session(session_id, username)
    
    # 2. Initialize history from the DB
    history = ChatHistory(messages=session.messages)

    # 3. Append the new user message if provided
    if request.message:
        history.add_message(request.message)

    
    # Initialize tools
    tools = [
        create_get_user_profile_tool(user_id="aaaa", db_connection="dummy-db"),
        create_weather_tool(location="Test, Testilandia"),
        
        # WikiEngine
        create_search_article_tool(wiki_instance),
        create_get_article_intro_tool(wiki_instance),
        create_get_article_section_tool(wiki_instance),
        create_get_article_infotable_tool(wiki_instance),

        # UI control
        fly_to_const_tool(),
        select_object_element_tool()
    ]

    # Return a StreamingResponse
    return StreamingResponse(
        sse_event_generator(history, tools, request.model, session_id, SYSTEM_PROMPT),
        media_type="text/event-stream"
    )
