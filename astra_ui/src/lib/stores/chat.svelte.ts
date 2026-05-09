import { chatAPI } from '$lib/api/chat';
import type { ChatSession, ChatMessage, ToolCall, ToolCallDefinition } from '$lib/types/chat';
import { selectionStore } from '$lib/stores/activeSelection.svelte';
import { catalogStore } from './skyCatalog.svelte';
import { locStore } from './location.svelte';
import { deviceStore } from './devices.svelte';

export type ChatAction = 
    | { type: 'focus_object', id: string, objectType: string }
    | { type: 'fly_to_constellation', abbr: string };

class ChatStore {
    // State runes
    session = $state<ChatSession | null>(null);
    messages = $state<ChatMessage[]>([]);
    isStreaming = $state(false);
    isLoading = $state(false);
    error = $state<string | null>(null);
    
    // Command queue for UI components (like the 3D SkyMap) to consume
    pendingActions = $state<ChatAction[]>([]);

    // Private state for stream cancellation
    private abortController: AbortController | null = null;

    async loadSession(observation_id: string) {
        this.isLoading = true;
        this.error = null;
        try {
            const sessionData = await chatAPI.getSession(observation_id);
            this.session = sessionData;
            // Initialize messages
            this.messages = sessionData.messages.filter(m => m.role !== 'system');
        } catch (e: any) {
            console.error("Error loading chat session:", e);
            this.error = e.message || "Failed to load chat session.";
        } finally {
            this.isLoading = false;
        }
    }

    async sendMessage(content: string) {
        if (!this.session) {
            this.error = "No active chat session.";
            return;
        }

        if (this.isStreaming) return; // Prevent concurrent sends

        this.error = null;
        this.isStreaming = true;
        this.abortController = new AbortController();

        // 1. Optimistically append the user message
        const userMsg: ChatMessage = { role: 'user', content };
        this.messages.push(userMsg);

        try {
            const stream = chatAPI.streamChat(
                this.session._id, 
                userMsg, 
                "astra_ai",
                selectionStore.targetId,
                locStore.effectiveActiveId,
                deviceStore.effectiveActiveId,
                deviceStore.activeComponents.telescope,
                this.abortController.signal
            );

            for await (const event of stream) {
                // Dynamically get the last message
                let lastMsg = this.messages[this.messages.length - 1];

                // If the event belongs to an assistant, but the last message isn't an assistant message, create a new one.
                if (['text', 'reasoning', 'tool_call_start', 'tool_call_chunk'].includes(event.event_type)) {
                    if (!lastMsg || lastMsg.role !== 'assistant') {
                        lastMsg = { role: 'assistant', content: '', reasoning_content: '', tool_calls: [] };
                        this.messages.push(lastMsg);
                    }
                }

                switch (event.event_type) {
                    case "text":
                        lastMsg.content = (lastMsg.content || '') + event.text;
                        break;
                    case "reasoning":
                        lastMsg.reasoning_content = (lastMsg.reasoning_content || '') + event.text;
                        break;
                    case "tool_call_start":
                        if (!lastMsg.tool_calls) lastMsg.tool_calls = [];
                        const fnDef: ToolCallDefinition = { name: event.tool_name, arguments: "" };
                        const newToolCall: ToolCall = {
                            id: event.tool_call_id,
                            type: "function",
                            function: fnDef
                        };
                        lastMsg.tool_calls.push(newToolCall);
                        break;
                    case "tool_call_chunk":
                        if (lastMsg.tool_calls && lastMsg.tool_calls.length > 0) {
                            // The chunk applies to the most recently started tool call
                            const lastToolCall = lastMsg.tool_calls[lastMsg.tool_calls.length - 1];
                            lastToolCall.function.arguments += event.chunk;
                        }
                        break;
                    case "tool_execution":
                        // Add the tool execution result to the chat history using the ChatMessage model
                        const toolExecutionMsg: ChatMessage = {
                            role: 'tool',
                            name: event.tool_name,
                            tool_call_id: event.tool_call_id,
                            content: JSON.stringify(event.result)
                        };
                        this.messages.push(toolExecutionMsg);
                        
                        if (event.result.frontend_action) {
                            this.handleFrontendAction(event.tool_name, event.arguments);
                        }
                        break;
                    case "error":
                        this.error = event.message;
                        console.error("Stream error event:", event.message, event.details);
                        break;
                    case "finish":
                        // Done streaming
                        break;
                }
            }
        } catch (e: any) {
            if (e.name === 'AbortError' || e.message?.includes('aborted')) {
                console.log("Chat stream aborted by user.");
            } else {
                console.error("Error during chat stream:", e);
                this.error = e.message || "An error occurred during chat.";
            }
        } finally {
            this.isStreaming = false;
            this.abortController = null;
        }
    }

    /**
     * Queues actions for the UI components to consume.
     */
    private handleFrontendAction(toolName: string, args: any) {
        console.info(`[Frontend Action Triggered]: ${toolName}`, args);
        
        try {
            const parsedArgs = typeof args === 'string' ? JSON.parse(args) : args;

            switch (toolName) {
                case 'focus_object':
                case 'slew_to_object':
                    if (parsedArgs && parsedArgs.id && parsedArgs.type) {
                        // Normalize planetary IDs to lowercase to bulletproof against LLM hallucinations
                        const objectId = parsedArgs.type === 'planetary' ? parsedArgs.id.toLowerCase() : parsedArgs.id;
                        
                        this.pendingActions.push({ 
                            type: 'focus_object', 
                            id: objectId, 
                            objectType: parsedArgs.type 
                        });
                    } else {
                        console.warn(`${toolName} tool called without valid id and type.`, parsedArgs);
                    }
                    break;
                case 'fly_to_constellation':
                    if (parsedArgs && parsedArgs.abbr) {
                        this.pendingActions.push({
                            type: 'fly_to_constellation',
                            abbr: parsedArgs.abbr
                        });
                    }
                    break;
                default:
                    console.warn(`No frontend handler implemented for tool: ${toolName}`);
            }
        } catch (e) {
            console.error(`Failed to handle frontend action for ${toolName}:`, e);
        }
    }

    consumeAction() {
        return this.pendingActions.shift();
    }

    abortStream() {
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
            this.isStreaming = false;
        }
    }

    reset() {
        this.abortStream();
        this.session = null;
        this.messages = [];
        this.pendingActions = [];
        this.error = null;
        this.isLoading = false;
    }
}

export const chatStore = new ChatStore();