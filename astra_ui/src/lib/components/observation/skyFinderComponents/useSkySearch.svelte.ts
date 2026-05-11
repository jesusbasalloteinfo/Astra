// src/lib/components/observation/skyFinderComponents/useSkySearch.svelte.ts
import { catalogStore } from '$lib/stores/skyCatalog.svelte';

export function createSkySearch(onSelect: (id: string, type: string) => void) {
    let searchQuery = $state('');
    let selectedIndex = $state(0);
    const results = $derived(catalogStore.searchObjects(searchQuery));

    // Reset selection when search query changes
    $effect(() => {
        // We use the getter here to track the dependency
        if (searchQuery) {
            selectedIndex = 0;
        }
    });

    function handleNavigation(e: KeyboardEvent) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, results.length - 1);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, 0);
        } else if (e.key === 'Enter' && results.length > 0) {
            e.preventDefault();
            const result = results[selectedIndex];
            onSelect(result.id, result.type);
        }
    }

    function clear() {
        searchQuery = '';
        selectedIndex = 0;
    }

    return {
        get searchQuery() { return searchQuery; },
        set searchQuery(v) { searchQuery = v; },
        get selectedIndex() { return selectedIndex; },
        set selectedIndex(v) { selectedIndex = v; },
        get results() { return results; },
        handleNavigation,
        clear
    };
}