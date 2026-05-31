// src/lib/components/observation/skyFinderComponents/useSkySearch.svelte.ts
import { catalogStore } from '$lib/stores/skyCatalog.svelte';

/**
 * Creates and manages the state for searching astronomical objects in the sky catalog.
 * Provides search query management, keyboard navigation for results, and selection handling.
 * 
 * @param {(id: string, type: string) => void} onSelect - Callback function called when an object is selected
 * @returns {Object} Search state and control functions
 */
export function createSkySearch(onSelect: (id: string, type: string) => void) {
    /** The current search query string */
    let searchQuery = $state('');

    /** The index of the currently highlighted result in the results list */
    let selectedIndex = $state(0);

    /** The list of objects matching the current search query, derived from the catalog store */
    const results = $derived(catalogStore.searchObjects(searchQuery));

    // Reset selection when search query changes
    $effect(() => {
        // We use the getter here to track the dependency
        if (searchQuery) {
            selectedIndex = 0;
        }
    });

    /**
     * Handles keyboard navigation (ArrowUp, ArrowDown, Enter) for search results
     * @param {KeyboardEvent} e - The keyboard event
     */
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

    /**
     * Clears the search query and resets the selection index
     */
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