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

<!-- src/lib/components/observationAssistant/ChatMessages.svelte -->
<script lang="ts">
    import { tick, onMount } from 'svelte';
    import { Bot, Sparkles, ArrowDown } from 'lucide-svelte';
    import { chatStore } from '$lib/stores/chat.svelte';
    import ChatMessageComponent from './ChatMessageComponent.svelte';
	import { m } from '$lib/paraglide/messages';

    /** Reference to the scrollable container for chat messages */
    let chatContainer = $state<HTMLElement>();

    /** Whether the user has scrolled up away from the bottom of the chat */
    let isScrolledUp = $state(false);

    /**
     * Handles the scroll event to determine if the user has scrolled up
     */
    function handleScroll() {
        if (!chatContainer) return;
        const distanceToBottom = chatContainer.scrollHeight - chatContainer.scrollTop - chatContainer.clientHeight;
        isScrolledUp = distanceToBottom > 50;
    }

    /**
     * Scrolls the chat container to the very bottom
     * @param {boolean} [smooth=true] - Whether to use smooth scrolling behavior
     */
    function scrollToBottom(smooth = true) {
        if (!chatContainer) return;
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: smooth ? 'smooth' : 'auto'
        });
        isScrolledUp = false;
    }

    // Auto-scroll
    $effect(() => {
        const msgs = chatStore.messages;
        const isStreaming = chatStore.isStreaming;
        const lastMsgContent = msgs[msgs.length - 1]?.content;

        tick().then(() => {
            // Scroll down if user hasn't scrolled up
            if (chatContainer && !isScrolledUp) {
                scrollToBottom(false); 
            }
        });
    });

    $effect(() => {
        if (chatContainer && chatStore.messages.length > 0) {
            setTimeout(() => scrollToBottom(false), 50);
        }
    });

    onMount(() => {
        if (!chatContainer) return;
        
        const observer = new ResizeObserver(() => {
            if (!isScrolledUp) {
                scrollToBottom(false);
            }
        });
        
        observer.observe(chatContainer);
        return () => observer.disconnect();
    });
</script>

<div class="relative flex-1 min-h-0 flex flex-col">
    
    <!-- Scrollable content -->
    <div 
        bind:this={chatContainer} 
        onscroll={handleScroll}
        class="h-full overflow-y-auto p-5 space-y-6 custom-scrollbar"
    >
        <!-- Empty state -->
        {#if chatStore.messages.length === 0}
            <div class="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-70">
                <div class="w-16 h-16 rounded-2xl bg-panel/30 border border-border flex items-center justify-center shadow-inner">
                    <Bot size={32} class="text-copy-muted" />
                </div>
                <div>
                    <h3 class="text-xs font-bold uppercase tracking-widest text-copy-primary">{m.obs_assistant_title()}</h3>
                    <p class="text-sm text-copy-muted mt-2 max-w-[16rem] mx-auto leading-relaxed">
                        {m.obs_assistant_empty()}
                    </p>
                </div>
            </div>
        {/if}

        <!-- Chat loop -->
        {#each chatStore.messages as msg, i}
            {@const isFirstInTurn = i === 0 || chatStore.messages[i - 1].role === 'user'}
            
            <ChatMessageComponent 
                {msg} 
                {isFirstInTurn} 
                isStreaming={chatStore.isStreaming}
                messagesContext={chatStore.messages}
            />
        {/each}

        <!-- Loading Indicator -->
        {#if chatStore.isStreaming && chatStore.messages[chatStore.messages.length - 1]?.role === 'user'}
            <div class="flex items-center gap-2 text-accent opacity-80">
                <Sparkles size={12} class="animate-pulse" />
                <span class="text-[9px] font-bold uppercase tracking-widest animate-pulse">{m.obs_assistant_loading()}</span>
            </div>
        {/if}
    </div>

    <!-- Scroll down button -->
    {#if isScrolledUp}
        <div class="absolute bottom-4 left-1/2 -translate-x-1/2 z-10">
            <button 
                onclick={() => scrollToBottom(true)}
                class="bg-surface/90 backdrop-blur-md border border-border text-accent hover:text-white hover:bg-accent hover:scale-105 hover:shadow-[0_0_15px_var(--color-accent-glow)] shadow-lg p-2 rounded-full transition-all duration-300 cursor-pointer flex items-center justify-center"
                title={m.obs_assistant_scrolldown()}
            >
                <ArrowDown size={16} />
            </button>
        </div>
    {/if}
</div>

<style>
    .custom-scrollbar {
        scrollbar-width: thin;
        scrollbar-color: var(--color-surface) transparent;
    }
    .custom-scrollbar::-webkit-scrollbar { width: 4px; }
    .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
    .custom-scrollbar::-webkit-scrollbar-thumb { background: var(--color-surface); border-radius: 10px; }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: var(--color-border); }
</style>