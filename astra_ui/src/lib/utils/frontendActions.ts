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

import type { FlyToConstellationArgs, FocusObjectArgs } from "$lib/types/tools";

/**
 * Represents an action triggered by the AI that needs to be handled by the UI.
 */
export type ChatAction = 
    | { type: 'focus_object', id: string, objectType: string }
    | { type: 'fly_to_constellation', abbr: string };



/**
 * Interface representing the UI context required to execute frontend actions.
 */
export interface ExecutionContext {
    /** The instance of the 3D SkyMap component */
    skyMap: any;
    /** The global selection store */
    selectionStore: any;
}

/**
 * Handlers for each type of ChatAction.
 */
const ACTION_HANDLERS: Record<string, (action: any, context: ExecutionContext) => void> = {
    focus_object: (action, { skyMap, selectionStore }) => {
        selectionStore.select(action.id, action.objectType as 'sidereal' | 'planetary');
        skyMap?.selectObject(action.id);
    },
    fly_to_constellation: (action, { skyMap }) => {
        skyMap?.flyToConstellation(action.abbr);
    }
};

/**
 * Executes a ChatAction using the provided UI context.
 * 
 * @param action - The action to execute.
 * @param context - The UI dependencies (skyMap, stores, etc.).
 */
export function executeFrontendAction(action: ChatAction, context: ExecutionContext) {
    const handler = ACTION_HANDLERS[action.type];
    if (handler) {
        handler(action, context);
    } else {
        console.warn(`[Frontend Action Dispatcher] No handler found for action type: ${action.type}`, action);
    }
}



// --- Action Constructors ---

/**
 * Creates a 'focus_object' ChatAction from tool arguments.
 * 
 * @param args - The tool arguments containing 'id' and 'type'.
 * @returns A ChatAction or null if required arguments are missing.
 */
export function getFocusObjectAction(args: FocusObjectArgs): ChatAction | null {
    if (args.id && args.type) {
        // Normalize planetary IDs to lowercase to bulletproof against LLM hallucinations
        return { 
            type: 'focus_object', 
            id: args.type === 'planetary' ? args.id.toLowerCase() : args.id, 
            objectType: args.type 
        };
    }
    return null;
}

/**
 * Creates a 'fly_to_constellation' ChatAction from tool arguments.
 * 
 * @param args - The tool arguments containing 'abbr'.
 * @returns A ChatAction or null if required arguments are missing.
 */
export function getFlyToConstellationAction(args: FlyToConstellationArgs): ChatAction | null {
    if (args.abbr) {
        return {
            type: 'fly_to_constellation',
            abbr: args.abbr
        };
    }
    return null;
}