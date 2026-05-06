import os
import json
import asyncio
from typing import List, Dict, Any, AsyncGenerator, Optional
from openai import AsyncOpenAI

from .models import (
    BaseToolResponse, ChatHistory, ChatMessage, ErrorEvent, ToolCall, ToolCallDefinition,
    ToolCallBuilder, ToolResult,
    SSEEvent, TextEvent, ReasoningEvent, ToolCallStartEvent, ToolCallChunkEvent, ToolExecutionEvent
)
from .tools import CurriedTool

client = AsyncOpenAI(
    base_url=os.getenv("LLM_API_BASE", "http://localhost:5000/v1"),
    api_key=os.getenv("LLM_API_KEY")
)

# --- Helper Functions ---

def _prepare_openai_kwargs(history: ChatHistory, tools: List[CurriedTool], model: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Converts the ChatHistory models into the raw dictionaries expected by OpenAI and prepares the kwargs"""

    messages = [msg.model_dump(exclude_none=True) for msg in history.messages]
    
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
        
    openai_tools = [tool.get_openai_tool_schema() for tool in tools]
    
    kwargs = {
        "model": model,
        "messages": messages,
        "stream": True,
        "reasoning_effort": "medium"
    }
    if openai_tools:
        kwargs["tools"] = openai_tools
    return kwargs

def _build_tool_calls_from_buffer(tool_calls_buffer: Dict[int, ToolCallBuilder]) -> List[ToolCall]:
    """Converts the toolcalls buffer to ToolCall objects."""

    assistant_tool_calls = []
    for _, builder in sorted(tool_calls_buffer.items()):
        assistant_tool_calls.append(
            ToolCall(
                id=builder.id,
                function=ToolCallDefinition(
                    name=builder.name,
                    arguments=builder.arguments
                )
            )
        )
    return assistant_tool_calls

async def _execute_single_tool(tc: ToolCall, tools_by_name: Dict[str, CurriedTool]) -> ToolResult:
    """Executes a single tool and formats its result."""
    
    tool_name = tc.function.name
    arguments_json = tc.function.arguments
    
    try:
        parsed_arguments = json.loads(arguments_json)
    except json.JSONDecodeError:
        parsed_arguments = arguments_json
    
    if tool_name in tools_by_name:
        curried_tool = tools_by_name[tool_name]
        result = await curried_tool.execute(arguments_json)
    else:
        result = BaseToolResponse(status="error", message=f"Error: Tool '{tool_name}' not found.")
        
    return ToolResult(
        tc_id=tc.id,
        tool_name=tool_name,
        result=result,
        arguments=parsed_arguments
    )

async def _execute_tools_concurrently(assistant_tool_calls: List[ToolCall], tools: List[CurriedTool]) -> List[ToolResult]:
    """Executes all requested tools at the same time"""

    tools_by_name = {t.name: t for t in tools}
    return await asyncio.gather(*(_execute_single_tool(tc, tools_by_name) for tc in assistant_tool_calls))


# --- MAIN STREAMING CORE ---

async def stream_chat(
    history: ChatHistory,
    tools: List[CurriedTool],
    model: str = "astra_ai",
    system_prompt: Optional[str] = None
) -> AsyncGenerator[SSEEvent, None]:
    """
    The main chat orchestrator. Streams responses, intercepts tool requests, executes them,
    and loops back to the LLM automatically.
    """
    
    # 1. Setup the Network Request
    kwargs = _prepare_openai_kwargs(history, tools, model, system_prompt)
    
    try:
        response = await client.chat.completions.create(**kwargs)

        # 2. Initialize State Buffers
        tool_calls_buffer: Dict[int, ToolCallBuilder] = {}
        assistant_content = ""
        assistant_reasoning_content = ""

        # 3. Async Stream parsing
        async for chunk in response:
            delta = chunk.choices[0].delta

            if getattr(delta, "reasoning_content", None) is not None:
                assistant_reasoning_content += delta.reasoning_content
                yield ReasoningEvent(text=delta.reasoning_content)

            if getattr(delta, "content", None) is not None:
                assistant_content += delta.content
                yield TextEvent(text=delta.content)

            # Parse and buffer tool calls. Because tools can be streamed in chunks
            # and multiple tools can be called, we use idx to group chunks by tool.
            if delta.tool_calls:
                for tc_chunk in delta.tool_calls:
                    idx = tc_chunk.index
                    
                    # If this is the first time we see this tool call index, initialize a builder for it.
                    if idx not in tool_calls_buffer:
                        tool_calls_buffer[idx] = ToolCallBuilder()
                    
                    builder = tool_calls_buffer[idx]
                    
                    # The ID is typically sent in the first chunk of a specific tool call.
                    if tc_chunk.id:
                        builder.id = tc_chunk.id
                    
                    # The function name is also typically sent in the first chunk.
                    # We yield a StartEvent so the frontend knows a specific tool has begun.
                    if tc_chunk.function and tc_chunk.function.name:
                        builder.name = tc_chunk.function.name
                        yield ToolCallStartEvent(tool_name=builder.name, tool_call_id=builder.id)
                    
                    # Arguments arrive in small string chunks over multiple SSE events.
                    # We append them to our builder's buffer and forward the raw chunk to the frontend.
                    if tc_chunk.function and tc_chunk.function.arguments:
                        arg_chunk = tc_chunk.function.arguments
                        builder.arguments += arg_chunk
                        yield ToolCallChunkEvent(chunk=arg_chunk)

    except asyncio.CancelledError:
        # Handle client disconnects or explicitly cancelled tasks.
        raise
    except Exception as e:
        # Handle Network, API, or general unexpected errors safely
        yield ErrorEvent(message="An error occurred while communicating with the LLM API.", details=str(e))
        return

    # 4. Post-Stream Actions to handle toolcalls and ending
    if tool_calls_buffer:
        
        # Save in history the received stream
        assistant_tool_calls = _build_tool_calls_from_buffer(tool_calls_buffer)
        history.add_message(ChatMessage(
            role="assistant",
            reasoning_content=assistant_reasoning_content if assistant_reasoning_content else None,
            content=assistant_content if assistant_content else None,
            tool_calls=assistant_tool_calls
        ))

        # Execute all the tools
        execution_results = await _execute_tools_concurrently(assistant_tool_calls, tools)

        # Process the results
        for result in execution_results:
            yield ToolExecutionEvent(
                tool_name=result.tool_name,
                arguments=result.arguments,
                result=result.result
            )
            history.add_message(ChatMessage(
                role="tool",
                content=json.dumps(result.result.model_dump(exclude_none=True)), # Stringify for the LLM
                tool_call_id=result.tc_id,
                name=result.tool_name
            ))

        # If not the end, recurse so the LLM can see the results and continue
        async for event in stream_chat(history=history, tools=tools, model=model, system_prompt=system_prompt):
            yield event
            
    else:
        # Base Case: No tools were called, save the assistant's final text.
        if assistant_content:
            history.add_message(ChatMessage(
                role="assistant",
                reasoning_content=assistant_reasoning_content if assistant_reasoning_content else None,
                content=assistant_content
            ))

