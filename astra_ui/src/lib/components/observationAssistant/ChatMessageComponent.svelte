<!--
  ASTRA - Automated Smart Telescope Remote Assistant
  Copyright (C) 2026 Jesus Basallote
  
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.
  
  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<!-- src/lib/components/observationAssistant/ChatMessageComponent.svelte -->
<script lang="ts">
    import { Sparkles, LoaderCircle, Wrench, Check, ChevronRight, TriangleAlert } from 'lucide-svelte';
    import { marked } from 'marked';
    import DOMPurify from 'isomorphic-dompurify';
    import type { ChatMessage } from '$lib/types/chat';
	import { slide } from 'svelte/transition';
    import { formatToolAction, getToolStatus } from './toolHelpers';
	import { authStore } from '$lib/stores/auth.svelte';
	import { m } from '$lib/paraglide/messages';
	import { toInlangBool } from '$lib/utils/i18n';

    /**
     * Component props
     * @type {{ msg: ChatMessage, isFirstInTurn: boolean, isStreaming: boolean, messagesContext: ChatMessage[] }}
     * @property {ChatMessage} msg - The message object to display
     * @property {boolean} isFirstInTurn - Whether this message is the first in an assistant's turn
     * @property {boolean} isStreaming - Whether the message content is currently being streamed
     * @property {ChatMessage[]} messagesContext - The full message history for context (e.g., finding tool results)
     */
    let { 
        msg, 
        isFirstInTurn, 
        isStreaming, 
        messagesContext 
    } = $props<{ 
        msg: ChatMessage, 
        isFirstInTurn: boolean, 
        isStreaming: boolean, 
        messagesContext: ChatMessage[] // Check the tools
    }>();

    /** Whether the assistant's reasoning block is expanded */
    let isReasoningOpen = $state(false);

    /** Whether to show tool debugging information */
    let enableToolDebug = $derived(import.meta.env.VITE_USER_DEBUG === 'true');

    // Marked config
    marked.use({ breaks: true, gfm: true });
    
    DOMPurify.addHook('afterSanitizeAttributes', function (node) {
        if (node.tagName === 'A') {
            node.setAttribute('target', '_blank');
            node.setAttribute('rel', 'noopener noreferrer');
        }
    });

    /**
     * Renders Markdown text into sanitized HTML
     * @param {string | undefined} text - The Markdown text to render
     * @returns {string} The sanitized HTML string
     */
    function renderMD(text: string | undefined) {
        if (!text) return '';
        const rawHtml = marked.parse(text, { async: false }) as string;
        return DOMPurify.sanitize(rawHtml);
    }
    
    /** Tracking which tool debug panels are open by their tool call ID */
    let openDebugTools = $state<Record<string, boolean>>({});

    /**
     * Toggles the visibility of a tool's debug information
     * @param {string} toolId - The unique ID of the tool call
     */
    function toggleToolDebug(toolId: string) {
        openDebugTools[toolId] = !openDebugTools[toolId];
    }

    /**
     * Parses a tool response string as JSON
     * @param {string} content - The raw string content from a tool message
     * @returns {any|null} The parsed object or null if parsing fails
     */
    function parseToolResponse(content: string) {
        try {
            return JSON.parse(content);
        } catch {
            return null;
        }
    }
    
</script>

{#if msg.role === 'user'}
    <!-- USER MESSAGE -->
     <div class="flex justify-end gap-2 text-accent/80 mb-1">
            <span class="text-[9px] font-bold uppercase tracking-widest">{authStore.user?.username}</span>
        </div>
    <div class="flex justify-end">
        <div class="bg-accent/10 border border-accent/20 text-copy-primary text-sm rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-[85%] shadow-inner wrap-break-word overflow-hidden">
            <div class="markdown-content">
                {@html renderMD(msg.content)}
            </div>
        </div>
    </div>
{:else if msg.role === 'assistant'}
    <!-- ASSISTANT MESSAGE -->
    <div class="flex flex-col gap-2 {isFirstInTurn ? '' : '-mt-3!'}">
        {#if isFirstInTurn}
            <div class="flex items-center gap-2 text-accent/80 mb-1">
                <Sparkles size={12} />
                <span class="text-[9px] font-bold uppercase tracking-widest">{m.obs_assistant_name()}</span>
            </div>
        {/if}
        
        <!-- Reasoning Content -->
        {#if msg.reasoning_content}
            {@const reasoningComplete = !!msg.content || !isStreaming}
            
            <div class="mb-2 flex flex-col gap-1.5">
                {#if reasoningComplete}
                    <button 
                        onclick={() => isReasoningOpen = !isReasoningOpen}
                        class="flex items-center gap-1.5 w-fit text-copy-muted hover:text-accent transition-colors cursor-pointer"
                    >
                        <ChevronRight size={14} class="transition-transform duration-200 {isReasoningOpen ? 'rotate-90' : ''}" />
                        <span class="text-[10px] font-bold uppercase tracking-wider">
                            {m.obs_assistant_thinking({thinking: toInlangBool(isReasoningOpen)})}
                        </span>
                    </button>
                {:else}
                    <div class="flex items-center gap-2 text-accent opacity-80 pl-1">
                        <LoaderCircle size={12} class="animate-spin" />
                        <span class="text-[10px] font-bold uppercase tracking-wider animate-pulse">{m.obs_assistant_loading()}</span>
                    </div>
                {/if}

                {#if !reasoningComplete || isReasoningOpen}
                    <div transition:slide={{ duration: 200 }} class="text-xs text-copy-muted/70 italic border-l-2 border-border/50 pl-3 py-1">
                        <div class="markdown-content">
                            {@html renderMD(msg.reasoning_content)}
                        </div>
                    </div>
                {/if}
            </div>
        {/if}

        <!-- Main Content -->
        {#if msg.content}
            <div class="text-sm text-copy-primary/90 leading-relaxed pr-4">
                <div class="markdown-content">
                    {@html renderMD(msg.content)}
                </div>
            </div>
        {/if}

        <!-- Tool Calls -->
        {#if msg.tool_calls && msg.tool_calls.length > 0}
            <div class="flex flex-col gap-1.5 mt-2">
                {#each msg.tool_calls as tool}
                    {@const toolMsg = messagesContext.find(m => m.role === 'tool' && m.tool_call_id === tool.id)}
                    {@const status = getToolStatus(messagesContext, tool.id)}
                    
                    
                    {@const borderColor = status === 'success' ? 'border-success/30' : status === 'error' ? 'border-danger/30' : 'border-border/50'}
                    {@const textColor = status === 'success' ? 'text-success/90' : status === 'error' ? 'text-danger/90' : 'text-copy-muted'}
                    
                    <div class="flex flex-col gap-1">
                        <div class="flex items-center gap-2 text-[10px] bg-panel/30 border {borderColor} rounded-lg px-2.5 py-1.5 w-fit shadow-inner transition-colors duration-500">
                            {#if status === 'success'}
                                <Check size={10} class={textColor} />
                            {:else if status === 'error'}
                                <TriangleAlert size={10} class={textColor} />
                            {:else if isStreaming}
                                <LoaderCircle size={10} class="animate-spin text-accent" />
                            {:else}
                                <Wrench size={10} class="text-copy-muted" />
                            {/if}                        
                            <span class="font-mono {textColor} uppercase tracking-wider">
                                {formatToolAction(tool.function.name, tool.function.arguments)}
                            </span>
                        </div>

                        <!-- Output debugging -->
                        {#if enableToolDebug && toolMsg}
                            <button 
                                onclick={() => toggleToolDebug(tool.id)}
                                class="flex items-center gap-1.5 w-fit text-copy-muted hover:text-accent transition-colors cursor-pointer mt-1"
                            >
                                <ChevronRight size={14} class="transition-transform duration-200 {openDebugTools[tool.id] ? 'rotate-90' : ''}" />
                                <span class="text-[10px] font-bold uppercase tracking-wider">
                                    {openDebugTools[tool.id] ? 'Hide' : 'Show'} Debug
                                </span>
                            </button>

                            {#if openDebugTools[tool.id]}
                                {@const parsed = parseToolResponse(toolMsg.content)}
                                
                                <div transition:slide={{ duration: 200 }} class="flex flex-col gap-2 mt-1.5 p-2.5 bg-secondary/30 border border-border/30 rounded-lg max-w-[90%] shadow-inner">
                                    
                                    {#if parsed}
                                        <!-- STATUS & FLAGS -->
                                        <div class="flex items-center gap-3 text-[10px] font-mono uppercase tracking-wider">
                                            <span class={parsed.status === 'success' ? 'text-success/90' : 'text-danger/90'}>
                                                Status: {parsed.status}
                                            </span>
                                            {#if parsed.frontend_action}
                                                <span class="text-accent bg-accent/10 px-1.5 py-0.5 rounded border border-accent/20">
                                                    Frontend Action
                                                </span>
                                            {/if}
                                        </div>

                                        <!-- MESSAGE (Renderizado como Markdown) -->
                                        {#if parsed.message}
                                            <div class="text-xs text-copy-primary/80 border-l-2 border-border/50 pl-2">
                                                <div class="markdown-content">
                                                    {@html renderMD(parsed.message)}
                                                </div>
                                            </div>
                                        {/if}

                                        <!-- DATA (JSON Formateado) -->
                                        {#if parsed.data}
                                            <div class="text-[10px] font-mono bg-panel/50 text-copy-muted p-2 rounded border border-border/30 overflow-x-auto custom-scrollbar">
                                                <pre><code>{JSON.stringify(parsed.data, null, 2)}</code></pre>
                                            </div>
                                        {/if}

                                    {:else}
                                        <!-- FALLBACK: Si por lo que sea no es JSON, mostramos el texto crudo -->
                                        <div class="text-[10px] font-mono text-copy-muted overflow-x-auto whitespace-pre-wrap custom-scrollbar">
                                            {toolMsg.content}
                                        </div>
                                    {/if}
                                </div>
                            {/if}
                        {/if}
                    </div>
                {/each}
            </div>
        {/if}
    </div>
{/if}