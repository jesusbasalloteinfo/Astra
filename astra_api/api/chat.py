import json
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.assistant import FinalEvent
from core.dependencies import get_request_user
from services.assistant import stream_chat, ChatHistory, ChatMessage
from services.tools.observation import fly_to_const_tool, focus_object_element_tool
from services.tools import *
from services.device_tunnel.tunnel import DeviceTunnel, tunnel_manager

from services.db.ChatSessionService import ChatSessionService
from services.db.UserService import UserService

router = APIRouter()
wiki_instance=WikiEngine(lang="en")

class StreamRequest(BaseModel):
    message: Optional[ChatMessage] = None
    model: str = "astra_ai"
    selected_obj: Optional[str] = None
    location_id: Optional[str] = None
    device_id: Optional[str] = None
    telescope: Optional[str] = None
    

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

    user_service = UserService()
    user_obj = await user_service.get_user(username)
    
    # Resolve location
    location = (0.0, 0.0) # Default
    if request.location_id:
        loc = next((l for l in user_obj.locations if l.id == request.location_id), None)
        if loc:
            location = (loc.lat, loc.lng)
    else:
        # Get default location
        loc = next((l for l in user_obj.locations if l.is_default), None)
        if loc:
            location = (loc.lat, loc.lng)
        elif user_obj.locations:
            location = (user_obj.locations[0].lat, user_obj.locations[0].lng)

    telescope_tools=[]
    if request.telescope:
        tunnel=tunnel_manager.get(request.device_id)

        telescope_tools = [            
            slew_to_object_tool(tunnel, request.telescope, location),
        ]

    
    # Initialize tools
    tools = [       
        # WikiEngine
        create_search_article_tool(wiki_instance),
        create_get_article_intro_tool(wiki_instance),
        create_get_article_section_tool(wiki_instance),
        create_get_article_infotable_tool(wiki_instance),

        # Sideris DB
        search_object_tool(),
        get_object_details_tool(location),

        # UI control
        fly_to_const_tool(),
        focus_object_element_tool()
    ]
    tools.extend(telescope_tools)

    # Return a StreamingResponse
    return StreamingResponse(
        sse_event_generator(history, tools, request.model, session_id, SYSTEM_PROMPT),
        media_type="text/event-stream"
    )
