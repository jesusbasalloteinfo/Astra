<!-- src/lib/components/simulator/SkyFinder.svelte -->
<script lang="ts">
    import { fade } from 'svelte/transition';
    import { Search, Star, Globe, ChevronRight } from 'lucide-svelte';
    import { catalogStore } from '$lib/stores/skyCatalog.svelte';
    import { selectionStore } from '$lib/stores/activeSelection.svelte';
	import { m } from '$lib/paraglide/messages';

    let { open = $bindable(), onSelect } = $props<{ 
        open: boolean;
        onSelect: (id: string) => void;
    }>();

    let searchQuery = $state('');
    let selectedIndex = $state(0);

    const results = $derived(catalogStore.searchObjects(searchQuery));

    // Reset selection when writting
    $effect(() => {
        if (searchQuery) selectedIndex = 0;
    });

    function selectObject(id: string, resultType: string) {
        const type = resultType === 'Planetary' ? 'planetary' : 'sidereal';
        selectionStore.select(id, type);
        
        if (onSelect) {
            onSelect(id);
        }

        searchQuery = '';
        open = false;
    }

    function handleKeydown(e: KeyboardEvent) {
        // Open
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'f') {
            e.preventDefault();
            open = true;
            return;
        }

        if (!open) return;

        // Navigate the list
        if (e.key === 'Escape') {
            open = false;
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, results.length - 1);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, 0);
        } else if (e.key === 'Enter' && results.length > 0) {
            e.preventDefault();
            const result = results[selectedIndex];
            selectObject(result.id, result.type);
        }
    }

    function setFocus(node: HTMLInputElement) {
        requestAnimationFrame(() => node.focus());
    }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
    <div transition:fade={{ duration: 150 }} class="absolute inset-0 z-50 flex items-start justify-center pt-32 pointer-events-auto">
        <button class="absolute inset-0 w-full h-full bg-black/60 backdrop-blur-sm cursor-default appearance-none border-none focus:outline-none" onclick={() => open = false} aria-label={m.obs_skyfinder_close()} tabindex="-1"></button>

        <div class="relative z-10 w-full max-w-2xl bg-surface backdrop-blur-xl border border-border rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden flex flex-col">
            
            <!-- Search bar -->
            <div class="flex items-center px-6 h-16 border-b border-border/50">
                <Search size={22} class="text-accent mr-4" />
                <input 
                    use:setFocus
                    bind:value={searchQuery}
                    type="text" 
                    placeholder={m.obs_skyfinder_placeholder()}
                    class="flex-1 bg-transparent border-none text-lg text-white focus:outline-none focus:ring-0 placeholder-copy-muted/50" 
                >
                <div class="flex items-center gap-2 ml-4">
                    <button onclick={() => open = false} class="cursor-pointer px-2 py-1 bg-panel/50 rounded-lg text-[10px] font-bold text-copy-muted hover:text-white border border-border/50 shadow-inner">ESC</button>
                </div>
            </div>

            <!-- Result list -->
            <div class="bg-panel/30 overflow-y-auto">
                {#if searchQuery.length < 2}
                    <div class="p-8 flex flex-col items-center justify-center text-center">
                        <Search size={32} class="text-copy-muted/30 mb-3" />
                        <p class="text-sm text-copy-muted font-medium">{m.obs_skyfinder_type()}</p>
                    </div>
                {:else if results.length === 0}
                    <div class="p-8 flex flex-col items-center justify-center text-center">
                        <p class="text-sm text-copy-muted font-medium">{m.obs_skyfinder_no_objects({query: searchQuery})}</p>
                    </div>
                {:else}
                    <div class="p-2">
                        {#each results as result, i}
                            <button 
                                onclick={() => selectObject(result.id, result.type)}
                                onmouseover={() => selectedIndex = i}
                                onfocus={() => selectedIndex = i}
                                class="w-full flex items-center justify-between p-3 rounded-xl transition-all cursor-pointer border border-transparent
                                    {selectedIndex === i ? 'bg-accent/20 border-accent/50 shadow-inner' : 'hover:bg-panel/50'}"
                            >
                                <div class="flex items-center gap-4">
                                    <div class="p-2 rounded-lg {selectedIndex === i ? 'bg-accent text-white shadow-[0_0_10px_var(--color-accent-glow)]' : 'bg-surface text-copy-muted'}">
                                        {#if result.type === 'Planetary'}
                                            <Globe size={16} />
                                        {:else}
                                            <Star size={16} />
                                        {/if}
                                    </div>
                                    <div class="text-left">
                                        <h4 class="text-sm font-bold {selectedIndex === i ? 'text-accent' : 'text-copy-primary'}">{result.name}</h4>
                                        <p class="text-[10px] text-copy-muted uppercase tracking-widest">{result.type} · Mag: {result.mag ?? 'N/A'}</p>
                                    </div>
                                </div>
                                <div class="flex items-center gap-2 text-copy-muted {selectedIndex === i ? 'opacity-100' : 'opacity-0'} transition-opacity">
                                    <span class="text-[9px] font-bold uppercase tracking-widest">{m.obs_skyfinder_select()}</span>
                                    <ChevronRight size={16} />
                                </div>
                            </button>
                        {/each}
                    </div>
                {/if}
            </div>
            
        </div>
    </div>
{/if}