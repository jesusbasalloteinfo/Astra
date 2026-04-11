<!-- src/lib/components/observationAssistant/Chat.svelte -->
<script lang="ts">
    import { slide } from 'svelte/transition';
    import { Sparkles, X } from 'lucide-svelte';
	import { m } from '$lib/paraglide/messages';
    let { open = $bindable() } = $props();
</script>

{#if open}
    <div transition:slide={{ axis: 'x', duration: 300 }} class="absolute top-0 right-0 h-full bg-surface/90 backdrop-blur-2xl border-l border-border shadow-[-10px_0_30px_rgba(0,0,0,0.5)] z-30 pointer-events-auto flex flex-col">
        <div class="h-16 flex items-center justify-between px-6 border-b border-border/50">
            <div class="flex items-center gap-2">
                <Sparkles size={18} class="text-purple-400" />
                <span class="font-bold tracking-widest text-sm uppercase">{m.obs_ai_title()}</span>
            </div>
            <button onclick={() => open = false} class="cursor-pointer p-2 hover:bg-panel/50 rounded-full text-copy-muted hover:text-white transition-colors">
                <X size={20} />
            </button>
        </div>
        <div class="flex-1 flex items-center justify-center p-6 text-center">
            <p class="text-copy-muted text-sm">Work in progress...</p>
        </div>
    </div>
{/if}