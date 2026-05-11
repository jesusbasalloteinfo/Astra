<!-- src/lib/components/observation/sideDockComponents/CommandPaletteShell.svelte -->
<script lang="ts">
    import { fade } from 'svelte/transition';
    import { m } from '$lib/paraglide/messages';

    let { 
        open = $bindable(false), 
        children,
        maxWidth = 'max-w-2xl'
    } = $props();

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            open = false;
        }
    }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
    <div transition:fade={{ duration: 150 }} class="absolute inset-0 z-50 flex items-start justify-center pt-16 md:pt-32 px-4 md:px-0 pointer-events-auto">
        <button 
            class="absolute inset-0 w-full h-full bg-black/60 backdrop-blur-sm cursor-default appearance-none border-none focus:outline-none" 
            onclick={() => open = false} 
            aria-label={m.obs_skyfinder_close()} 
            tabindex="-1"
        ></button>

        <div class="relative z-10 w-full {maxWidth} max-h-[80vh] md:max-h-[60vh] bg-surface backdrop-blur-xl border border-border rounded-2xl md:rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden flex flex-col">
            {@render children()}
        </div>
    </div>
{/if}