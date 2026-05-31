/**
 * Represents the definition of a tool call, including its name and stringified arguments.
 */
export interface ToolCallDefinition {
    /** The name of the function to be called. */
    name: string;
    /** JSON-stringified arguments for the function. */
    arguments: string;
}

/**
 * Represents a tool call request from the assistant.
 */
export interface ToolCall {
    /** Unique identifier for the tool call. */
    id: string;
    /** The type of tool call (currently only "function"). */
    type: "function";
    /** The details of the function to call. */
    function: ToolCallDefinition;
}

/**
 * Base structure for the response returned by a tool execution.
 */
export interface BaseToolResponse {
    /** Whether the tool execution was successful or failed. */
    status: "success" | "error";
    /** Optional human-readable message from the tool. */
    message?: string;
    /** Optional data returned by the tool. */
    data?: any;
    /** Whether this tool response requires an action from the frontend. */
    frontend_action?: boolean;
}

/**
 * Represents a single message in a chat session.
 */
export interface ChatMessage {
    /** The role of the message sender. */
    role: "system" | "user" | "assistant" | "tool";
    /** The internal reasoning/thought process of the assistant (optional). */
    reasoning_content?: string;
    /** The text content of the message. */
    content?: string;
    /** List of tool calls initiated by this message (for assistant role). */
    tool_calls?: ToolCall[];
    /** The ID of the tool call this message is responding to (for tool role). */
    tool_call_id?: string;
    /** The name of the tool (optional). */
    name?: string;
}

/**
 * Represents a full chat session history.
 */
export interface ChatSession {
    /** Unique identifier for the chat session. */
    _id: string;
    /** The ID of the observation session this chat belongs to. */
    observation_id: string;
    /** Human-readable title of the chat session. */
    title: string;
    /** List of messages in the session. */
    messages: ChatMessage[];
    /** ISO 8601 timestamp of creation. */
    created_at: string;
    /** ISO 8601 timestamp of the last update. */
    updated_at: string;
}

/**
 * Base interface for all Server-Sent Events (SSE) in the chat stream.
 */
export interface BaseSSEEvent {
    /** The type of the SSE event. */
    event_type: string;
}

/**
 * SSE event containing a chunk of text content.
 */
export interface TextEvent extends BaseSSEEvent {
    /** discriminator for text event. */
    event_type: "text";
    /** The text chunk. */
    text: string;
}

/**
 * SSE event containing a chunk of reasoning/thought process content.
 */
export interface ReasoningEvent extends BaseSSEEvent {
    /** discriminator for reasoning event. */
    event_type: "reasoning";
    /** The reasoning text chunk. */
    text: string;
}

/**
 * SSE event indicating the start of a tool call.
 */
export interface ToolCallStartEvent extends BaseSSEEvent {
    /** discriminator for tool call start. */
    event_type: "tool_call_start";
    /** The name of the tool being called. */
    tool_name: string;
    /** Unique identifier for this tool call. */
    tool_call_id: string;
}

/**
 * SSE event containing a chunk of tool call arguments.
 */
export interface ToolCallChunkEvent extends BaseSSEEvent {
    /** discriminator for tool call chunk. */
    event_type: "tool_call_chunk";
    /** The chunk of JSON-stringified arguments. */
    chunk: string;
}

/**
 * SSE event indicating that a tool has finished execution and providing the result.
 */
export interface ToolExecutionEvent extends BaseSSEEvent {
    /** discriminator for tool execution result. */
    event_type: "tool_execution";
    /** Unique identifier for the tool call. */
    tool_call_id: string;
    /** The name of the executed tool. */
    tool_name: string;
    /** The final arguments used for the tool call. */
    arguments?: any;
    /** The result returned by the tool. */
    result: BaseToolResponse;
}

/**
 * SSE event indicating an error occurred during the stream.
 */
export interface ErrorEvent extends BaseSSEEvent {
    /** discriminator for error event. */
    event_type: "error";
    /** Error message. */
    message: string;
    /** Optional detailed error information. */
    details?: string;
}

/**
 * SSE event indicating the end of the stream.
 */
export interface FinalEvent extends BaseSSEEvent {
    /** discriminator for finish event. */
    event_type: "finish";
}

/**
 * Union type of all possible SSE events in the chat stream.
 */
export type ChatSSEEvent = 
    | TextEvent 
    | ReasoningEvent 
    | ToolCallStartEvent 
    | ToolCallChunkEvent 
    | ToolExecutionEvent 
    | ErrorEvent 
    | FinalEvent;
