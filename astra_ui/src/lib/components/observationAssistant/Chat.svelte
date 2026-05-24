<!-- src/lib/components/observationAssistant/Chat.svelte -->
<script lang="ts">
    import { slide, fade, fly } from 'svelte/transition';
    import { Sparkles, X, Target } from 'lucide-svelte';
    import { m } from '$lib/paraglide/messages';
    
    import { chatStore } from '$lib/stores/chat.svelte'; 
    import { selectionStore } from '$lib/stores/activeSelection.svelte';
    import { activeObs } from '$lib/stores/activeObservation.svelte'; 

    import ChatMessages from './ChatMessages.svelte';
    import ChatInput from './ChatInput.svelte';
	import { untrack, onMount } from 'svelte';

    let { open = $bindable(), onClear  } = $props<{ 
        open: boolean; 
        onClear: () => void; 
    }>();

    let isPortrait = $state(false);

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

    onMount(() => {
        const updateMedia = () => {
            isPortrait = window.matchMedia("(orientation: portrait)").matches;
        };
        updateMedia();
        window.addEventListener("resize", updateMedia);
        return () => window.removeEventListener("resize", updateMedia);
    });
    
</script>

{#if open}
    <div 
        transition:fly={isPortrait ? { y: 1000, duration: 400 } : { x: 500, duration: 400 }} 
        class="absolute inset-0 z-50 w-full h-[100dvh] bg-surface/95 backdrop-blur-2xl border-border shadow-[-10px_0_30px_rgba(0,0,0,0.5)] pointer-events-auto flex flex-col
               {isPortrait ? 'border-t' : 'border-l landscape:md:inset-auto landscape:md:top-0 landscape:md:right-0 landscape:md:h-full landscape:md:w-[40vw] landscape:md:z-30 lg:landscape:w-120'}">        
        
        <!-- HEADER -->
        <div class="h-16 flex items-center justify-between px-6 border-b border-border/50 shrink-0">
            <div class="flex items-center gap-2 drop-shadow-[0_0_5px_rgba(168,85,247,0.5)]">
                <Sparkles size={18} class="text-purple-400" />
                <span class="font-bold tracking-widest text-[11px] uppercase text-copy-primary">{m.obs_assistant_title()}</span>
            </div>
            <button onclick={() => open = false} class="cursor-pointer p-2 hover:bg-panel/50 rounded-full text-copy-muted hover:text-white transition-colors">
                <X size={22} />
            </button>
        </div>

        <!-- ACTIVE TARGET CONTEXT -->
        {#if selectionStore.targetDetails}
            <div class="shrink-0 bg-accent/5 border-b border-accent/10 px-6 py-3 flex items-center justify-between">
                <div class="flex items-center gap-2 text-xs">
                    <Target size={14} class="text-accent animate-pulse" />
                    <span class="text-[9px] uppercase tracking-widest text-copy-muted">{m.obs_assistant_target()}</span>
                    <span class="text-accent font-bold truncate max-w-48">{selectionStore.targetDetails.name}</span>
                </div>
                <button onclick={onClear} class="text-copy-muted hover:text-white transition-colors p-1">
                    <X size={14} />
                </button>
            </div>
        {/if}

        <!-- SUB-COMPONENTS -->
        <ChatMessages />
        <ChatInput />

    </div>
{/if}