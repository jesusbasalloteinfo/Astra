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


export function formatToolAction(toolName: string, argsString: string) {
    // Format the tool titles depending on the tool
    try {
        const args = JSON.parse(argsString || '{}');
        
        switch (toolName) {
            case 'search_wiki_articles':
                return `Search in wiki: ${args.text || '...'}`;
            case 'slew_telescope':
                return `Pointing to RA:${args.ra} DEC:${args.dec}`;
            case 'focus_object':
                return 'Centering target'
            case 'fly_to_constellation':
                return 'Centering constellation'
            case 'sideris_search_object':
                return 'Searching objects...'    
            case 'sideris_get_object_details':
                return 'Consulting object...'
            case 'get_wiki_article_intro':
                return 'Get intro'
            default:
                // No case, no problem!
                return toolName.replace(/_/g, ' '); 
        }
    } catch {
        return toolName;
    }
}

export function getToolStatus(messages, toolId: string): 'pending' | 'success' | 'error' {
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
