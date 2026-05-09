
export function formatToolAction(toolName: string, argsString: string) {
    // Format the tool titles depending on the tool
    try {
        const args = JSON.parse(argsString || '{}');
        
        switch (toolName) {
            case 'search_articles':
                return `Search: ${args.text || '...'}`;
            case 'point_telescope':
                return `Pointing to RA:${args.ra} DEC:${args.dec}`;
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
