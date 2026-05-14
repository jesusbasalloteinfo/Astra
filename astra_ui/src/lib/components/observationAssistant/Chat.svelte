<!-- src/lib/components/observationAssistant/Chat.svelte -->
<script lang="ts">
    import { slide } from 'svelte/transition';
    import { Sparkles, X, Target } from 'lucide-svelte';
    import { m } from '$lib/paraglide/messages';
    
    import { chatStore } from '$lib/stores/chat.svelte'; 
    import { selectionStore } from '$lib/stores/activeSelection.svelte';
    import { activeObs } from '$lib/stores/activeObservation.svelte'; 

    import ChatMessages from './ChatMessages.svelte';
    import ChatInput from './ChatInput.svelte';
	import { untrack } from 'svelte';

    let { open = $bindable(), onClear  } = $props<{ 
        open: boolean; 
        onClear: () => void; 
    }>();

    $effect(() => {
        const isOpen = open;
        const targetObsId = activeObs.current?.id;
        if (isOpen && targetObsId) {
            untrack(() => {
                const currentSessionObsId = chatStore.session?.observation_id;
                const isStoreLoading = chatStore.isLoading;
                chatStore.loadSession(targetObsId);
            });
        }
    });
    
</script>

{#if open}
    <div transition:slide={{ axis: 'x', duration: 300 }} class="absolute top-0 right-0 h-full w-120 bg-surface/90 backdrop-blur-2xl border-l border-border shadow-[-10px_0_30px_rgba(0,0,0,0.5)] z-30 pointer-events-auto flex flex-col">        
        
        <!-- HEADER -->
        <div class="h-16 flex items-center justify-between px-5 border-b border-border/50 shrink-0">
            <div class="flex items-center gap-2 drop-shadow-[0_0_5px_rgba(168,85,247,0.5)]">
                <Sparkles size={16} class="text-purple-400" />
                <span class="font-bold tracking-widest text-[10px] uppercase text-copy-primary">{m.obs_assistant_title()}</span>
            </div>
            <button onclick={() => open = false} class="cursor-pointer p-1.5 hover:bg-panel/50 rounded-full text-copy-muted hover:text-white transition-colors">
                <X size={18} />
            </button>
        </div>

        <!-- ACTIVE TARGET CONTEXT -->
        {#if selectionStore.targetDetails}
            <div class="shrink-0 bg-accent/5 border-b border-accent/10 px-5 py-2.5 flex items-center justify-between">
                <div class="flex items-center gap-2 text-xs">
                    <Target size={14} class="text-accent animate-pulse" />
                    <span class="text-[9px] uppercase tracking-widest text-copy-muted">{m.obs_assistant_target()}</span>
                    <span class="text-accent font-bold truncate max-w-48">{selectionStore.targetDetails.name}</span>
                </div>
                <button onclick={onClear} class="text-copy-muted hover:text-white transition-colors">
                    <X size={12} />
                </button>
            </div>
        {/if}

        <!-- SUB-COMPONENTS -->
        <ChatMessages />
        <ChatInput />

    </div>
{/if}