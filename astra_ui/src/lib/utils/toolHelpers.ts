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


import * as m from "$lib/paraglide/messages.js";
import { getFlyToConstellationAction, getFocusObjectAction, type ChatAction } from "$lib/utils/frontendActions";
import type { 
    FlyToConstellationArgs, 
    FocusObjectArgs, 
    GetWikiArticleArgs, 
    GetWikiSectionArgs, 
    SearchObjectArgs, 
    SearchWikiArgs, 
    SlewToArgs 
} from "$lib/types/tools";


/**
 * Defines the structure and behavior of a tool within the assistant's registry.
 * Each tool can specify how its status messages are formatted and whether it
 * triggers a frontend action (like moving the map).
 */
export interface ToolDefinition<T = any>{

    /** Whether the user can manually trigger this tool again (e.g., via a "Repeat" button) */
    isReplayable: boolean;
    /** Function to format the human-readable message displayed in the chat for this tool call */
    formatMessage: (args: T) => string;
    /** Optional factory function to create a ChatAction from the tool arguments */
    getFrontendAction?: (args: T) => ChatAction | null;
}

/**
 * Central registry for all tools supported by the UI.
 * This maps technical tool names to their display logic and frontend behaviors.
 */
export const TOOL_REGISTRY: Record<string, ToolDefinition> = {
    'sideris_search_object': {
        isReplayable: false,
        formatMessage: (args: SearchObjectArgs) => m.tool_sideris_search_object()
    },
    'sideris_get_object_details': {
        isReplayable: false,
        formatMessage: () => m.tool_sideris_get_object_details()
    },
    'search_wiki_articles': {
        isReplayable: false,
        formatMessage: (args: SearchWikiArgs) => m.tool_search_wiki_articles({ query: args.query || '...' })
    },
    'get_wiki_article_intro': {
        isReplayable: false,
        formatMessage: (args: GetWikiArticleArgs) => m.tool_get_wiki_article_intro()
    },
    'get_wiki_article_section': {
        isReplayable: false,
        formatMessage: (args: GetWikiSectionArgs) => m.tool_get_wiki_article_section()
    },
    'get_wiki_article_infotable': {
        isReplayable: false,
        formatMessage: (args: GetWikiArticleArgs) => m.tool_get_wiki_article_infotable()
    },
    'focus_object': {
        isReplayable: true,
        formatMessage: (args: FocusObjectArgs) => m.tool_focus_object({ object: args.name || args.id || '...' }),
        getFrontendAction: (args: FocusObjectArgs) => getFocusObjectAction(args)
    },
    'fly_to_constellation': {
        isReplayable: true,
        formatMessage: (args: FlyToConstellationArgs) => m.tool_fly_to_constellation({ constellation: args.name || args.abbr || '...' }),
        getFrontendAction: (args: FlyToConstellationArgs) => getFlyToConstellationAction(args)
    },
    'slew_telescope': {
        isReplayable: false,
        formatMessage: (args: SlewToArgs) => m.tool_slew_telescope({ target: args.name || args.id || '...' }),
        getFrontendAction: (args: SlewToArgs) => getFocusObjectAction(args)
    }

}

/**
 * Formats a technical tool call into a localized, human-readable action description.
 * 
 * @param toolName - The identifier of the tool (e.g., 'slew_telescope').
 * @param argsString - The JSON string containing the tool arguments.
 * @returns A formatted string or the technical name if no registry entry exists.
 */
export function formatToolAction(toolName: string, argsString: string) {
    // Format the tool titles depending on the tool
    try {
        const args = JSON.parse(argsString || '{}');
        const toolDef = TOOL_REGISTRY[toolName];
        if (!toolDef) {
            // No case, no problem! Fallback to technical name
            return toolName.replace(/_/g, ' ');    
        }
        return toolDef.formatMessage(args);         
    } catch {
        return toolName;
    }
}

/**
 * Determines the execution status of a specific tool call by searching through
 * the conversation history for the corresponding tool response message.
 * 
 * @param messages - The full list of chat messages.
 * @param toolId - The unique ID of the tool call to check.
 * @returns 'pending' if no result is found, 'success' or 'error' based on the response content.
 */
export function getToolStatus(messages: any[], toolId: string): 'pending' | 'success' | 'error' {
    // Get the tools completion status

    const toolMsg = messages.find(m => m.role === 'tool' && m.tool_call_id === toolId);

    if (!toolMsg) return 'pending';

    try {
        const parsed = JSON.parse(toolMsg.content);
        return parsed.status === 'error' ? 'error' : 'success';
    } catch {
        return 'success';
    }
}
