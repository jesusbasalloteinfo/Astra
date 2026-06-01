/*
 * ASTRA - Automated Smart Telescope Remote Assistant
 * Copyright (C) 2026 Jesus Basallote
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

// lib/api/chat.ts
import { api } from './client';
import { endpoints } from './endpoints';
import type { ChatSession, ChatMessage, ChatSSEEvent } from '../types/chat';

/**
 * Chat API module for managing chat sessions and streaming AI responses.
 */
export const chatAPI = {
    /**
     * Retrieves or creates a chat session for a specific observation.
     * @param {string} observation_id - The unique identifier of the observation.
     * @returns {Promise<ChatSession>} The retrieved or newly created chat session.
     */
    getSession: async (observation_id: string): Promise<ChatSession> => {
        const response = await api.get<ChatSession>(endpoints.chat.session(observation_id));
        return response.data;
    },

    /**
     * Streams a chat response from the AI assistant using Server-Sent Events (SSE).
     * @param {string} session_id - The unique identifier of the chat session.
     * @param {ChatMessage | null} message - The message object to send to the AI.
     * @param {string} [model="astra_ai"] - The AI model to use for the response.
     * @param {string | null} [selected_obj=null] - Optional ID of a selected astronomical object.
     * @param {string | null} [location_id=null] - Optional ID of the user's location.
     * @param {string | null} [device_id=null] - Optional ID of the connected device.
     * @param {string | null} [telescope=null] - Optional name or ID of the telescope.
     * @param {AbortSignal} [signal] - Optional signal to abort the streaming request.
     * @yields {ChatSSEEvent} A stream of chat events including content chunks and status updates.
     * @returns {AsyncGenerator<ChatSSEEvent, void, unknown>}
     */
    streamChat: async function* (session_id: string, 
                                message: ChatMessage | null, 
                                model: string = "astra_ai", 
                                selected_obj: string | null = null,
                                location_id: string | null = null,
                                device_id: string | null = null,
                                telescope: string | null = null,                               
                                signal?: AbortSignal): AsyncGenerator<ChatSSEEvent, void, unknown> {
        console.log("Sending message to LLM with: ", { message, model, selected_obj, location_id, device_id, telescope })
        const response = await api.post(endpoints.chat.stream(session_id), 
            { message, model, selected_obj, location_id, device_id, telescope }, 
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
