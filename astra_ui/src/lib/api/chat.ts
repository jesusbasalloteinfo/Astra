import { api } from './client';
import { endpoints } from './endpoints';
import type { ChatSession, ChatMessage, ChatSSEEvent } from '../types/chat';

export const chatAPI = {
    // Get or create a chat session for a given observation
    getSession: async (observation_id: string): Promise<ChatSession> => {
        const response = await api.get<ChatSession>(endpoints.chat.session(observation_id));
        return response.data;
    },

    // Stream chat response
    streamChat: async function* (session_id: string, message: ChatMessage | null, model: string = "astra_ai", signal?: AbortSignal): AsyncGenerator<ChatSSEEvent, void, unknown> {
        const response = await api.post(endpoints.chat.stream(session_id), 
            { message, model }, 
            {
                responseType: 'stream',
                signal: signal
            }
        );

        const stream = response.data as ReadableStream<Uint8Array>;
        const reader = stream.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            
            // Keep the last incomplete chunk in the buffer
            buffer = lines.pop() || "";

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const dataStr = line.slice(6).trim();
                    if (!dataStr) continue;
                    try {
                        const event = JSON.parse(dataStr) as ChatSSEEvent;
                        yield event;
                    } catch (e) {
                        console.error("Failed to parse SSE JSON:", dataStr, e);
                    }
                }
            }
        }
    }
};
