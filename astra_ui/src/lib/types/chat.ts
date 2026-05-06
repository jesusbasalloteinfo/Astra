export interface ToolCallDefinition {
    name: string;
    arguments: string;
}

export interface ToolCall {
    id: string;
    type: "function";
    function: ToolCallDefinition;
}

export interface BaseToolResponse {
    status: "success" | "error";
    message?: string;
    data?: any;
    frontend_action?: boolean;
}

export interface ChatMessage {
    role: "system" | "user" | "assistant" | "tool";
    reasoning_content?: string;
    content?: string;
    tool_calls?: ToolCall[];
    tool_call_id?: string;
    name?: string;
}

export interface ChatSession {
    _id: string;
    observation_id: string;
    title: string;
    messages: ChatMessage[];
    created_at: string;
    updated_at: string;
}

export interface BaseSSEEvent {
    event_type: string;
}

export interface TextEvent extends BaseSSEEvent {
    event_type: "text";
    text: string;
}

export interface ReasoningEvent extends BaseSSEEvent {
    event_type: "reasoning";
    text: string;
}

export interface ToolCallStartEvent extends BaseSSEEvent {
    event_type: "tool_call_start";
    tool_name: string;
    tool_call_id: string;
}

export interface ToolCallChunkEvent extends BaseSSEEvent {
    event_type: "tool_call_chunk";
    chunk: string;
}

export interface ToolExecutionEvent extends BaseSSEEvent {
    event_type: "tool_execution";
    tool_name: string;
    arguments?: any;
    result: BaseToolResponse;
}

export interface ErrorEvent extends BaseSSEEvent {
    event_type: "error";
    message: string;
    details?: string;
}

export interface FinalEvent extends BaseSSEEvent {
    event_type: "finish";
}

export type ChatSSEEvent = 
    | TextEvent 
    | ReasoningEvent 
    | ToolCallStartEvent 
    | ToolCallChunkEvent 
    | ToolExecutionEvent 
    | ErrorEvent 
    | FinalEvent;

