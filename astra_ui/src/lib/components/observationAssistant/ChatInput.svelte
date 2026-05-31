<!-- src/lib/components/observationAssistant/ChatInput.svelte -->
<script lang="ts">
    import { Send, Square } from 'lucide-svelte';
    import { chatStore } from '$lib/stores/chat.svelte';
	import { m } from '$lib/paraglide/messages';

    /** The current message being typed by the user */
    let inputMessage = $state('');

    /**
     * Sends the current input message to the chat store
     */
    function handleSend() {
        if (!inputMessage.trim() || chatStore.isStreaming) return;
        chatStore.sendMessage(inputMessage.trim());
        inputMessage = '';
    }

    /**
     * Handles keyboard events in the input field, specifically for sending on Enter
     * @param {KeyboardEvent} e - The keyboard event object
     */
    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }
</script>

<div class="p-4 shrink-0">
    <div class="relative flex items-end gap-2 bg-panel/30 border border-border focus-within:border-accent/50 rounded-2xl p-1.5 shadow-inner transition-colors">
        
        <textarea 
            bind:value={inputMessage}
            onkeydown={handleKeydown}
            placeholder={m.obs_assistant_input_placeholder()}
            rows="1"
            class="w-full bg-transparent border-none text-sm text-copy-primary placeholder-copy-muted focus:ring-0 resize-none px-3 py-2 custom-scrollbar min-h-10 max-h-30"
            style="field-sizing: content;" 
        ></textarea>

        {#if chatStore.isStreaming}
            <button 
                onclick={() => chatStore.abortStream()}
                class="shrink-0 w-10 h-10 flex items-center justify-center bg-danger-surface text-danger hover:bg-danger/30 rounded-xl transition-colors cursor-pointer"
                title={m.obs_assistant_abort()}
            >
                <Square size={16} fill="currentColor" />
            </button>
        {:else}
            <button 
                onclick={handleSend}
                disabled={!inputMessage.trim()}
                title={m.obs_assistant_send()}
                class="shrink-0 w-10 h-10 flex items-center justify-center rounded-xl transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed
                {inputMessage.trim() ? 'bg-accent text-white shadow-[0_0_15px_var(--color-accent-glow)]' : 'bg-surface text-copy-muted'}"
            >
                <Send size={16} class="mr-0.5 mt-0.5" /> 
            </button>
        {/if}
    </div>
    
    {#if chatStore.error}
        <div class="mt-2 text-[10px] text-danger text-center uppercase tracking-widest font-bold">
            {m.obs_assistant_error({reason: chatStore.error})}
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