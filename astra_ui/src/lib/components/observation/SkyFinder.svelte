<!-- src/lib/components/observation/SkyFinder.svelte -->
<script lang="ts">
    import { Search } from 'lucide-svelte';
    import { selectionStore } from '$lib/stores/activeSelection.svelte';
	import { m } from '$lib/paraglide/messages';
    import CommandPaletteShell from './CommandPaletteShell.svelte';
    import SkyFinderResult from './skyFinderComponents/SkyFinderResult.svelte';
    import { createSkySearch } from './skyFinderComponents/useSkySearch.svelte';

    let { open = $bindable(), onSelect } = $props<{ 
        open: boolean;
        onSelect: (id: string) => void;
    }>();

    const search = createSkySearch((id, type) => {
        selectObject(id, type);
    });

    function selectObject(id: string, type: string) {
        if (type !== 'constellation') {
            selectionStore.select(id, type as 'sidereal' | 'planetary');
        }
        
        if (onSelect) {
            onSelect(id);
        }

        search.clear();
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

        // Delegate navigation to the rune
        search.handleNavigation(e);
    }

    function setFocus(node: HTMLInputElement) {
        requestAnimationFrame(() => node.focus());
    }
</script>

<svelte:window onkeydown={handleKeydown} />

<CommandPaletteShell bind:open>
    <!-- Search bar -->
    <div class="flex items-center px-6 h-16 border-b border-border/50">
        <Search size={22} class="text-accent mr-4" />
        <input 
            use:setFocus
            bind:value={search.searchQuery}
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
        {#if search.searchQuery.length < 2}
            <div class="p-8 flex flex-col items-center justify-center text-center">
                <Search size={32} class="text-copy-muted/30 mb-3" />
                <p class="text-sm text-copy-muted font-medium">{m.obs_skyfinder_type()}</p>
            </div>
        {:else if search.results.length === 0}
            <div class="p-8 flex flex-col items-center justify-center text-center">
                <p class="text-sm text-copy-muted font-medium">{m.obs_skyfinder_no_objects({query: search.searchQuery})}</p>
            </div>
        {:else}
            <div class="p-2">
                {#each search.results as result, i}
                    <SkyFinderResult 
                        {result}
                        isSelected={search.selectedIndex === i}
                        onclick={() => selectObject(result.id, result.type)}
                        onHover={() => search.selectedIndex = i}
                    />
                {/each}
            </div>
        {/if}
    </div>
</CommandPaletteShell>