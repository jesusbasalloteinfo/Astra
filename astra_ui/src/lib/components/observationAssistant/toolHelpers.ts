
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
