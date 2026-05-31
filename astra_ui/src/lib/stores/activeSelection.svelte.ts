// src/lib/stores/activeSelection.svelte.ts
import { siderisAPI } from '$lib/api/sideris';
import type { SiderealObjectDetails, PlanetaryObjectDetails } from '$lib/types/sideris';
import { locStore } from './location.svelte';
import { timeEngine } from './timeEngine.svelte';
import { getLocale } from '$lib/paraglide/runtime';

/**
 * Store for managing the currently selected celestial object and its details.
 * Automatically updates details when the time drifts significantly.
 */
class ActiveSelection {
    /** ID of the currently selected target. */
    targetId = $state<string | null>(null);
    /** Type of the currently selected target. */
    targetType = $state<'sidereal' | 'planetary' | null>(null);
    /** Detailed information about the selected target. */
    targetDetails = $state<SiderealObjectDetails | PlanetaryObjectDetails | null>(null);
    /** Loading state for fetching target details. */
    isLoadingDetails = $state(false);

    /** Timestamp of the last successful details fetch. */
    private lastFetchTime: number = 0;

    /**
     * Initializes the store and sets up an effect to automatically refresh object details
     * when time drifts by more than 5 minutes.
     */
    constructor() {
        if (typeof window !== 'undefined') {
            $effect.root(() => {
                $effect(() => {
                    // Reactive dependency on time and ID
                    const id = this.targetId;
                    const type = this.targetType;
                    const currentTime = timeEngine.current;
                    
                    if (!id || !type) return;

                    // If time has drifted more than 5 minutes since last fetch, update details
                    // Also updates if we change target
                    const currentMs = currentTime.getTime();
                    const deltaMs = Math.abs(currentMs - this.lastFetchTime);
                    
                    if (deltaMs > 5 * 60 * 1000) {
                        this.fetchDetails(id, type);
                    }
                });
            });
        }
    }

    /**
     * Selects a celestial object and fetches its details.
     * 
     * @param id - The ID of the object to select.
     * @param type - The type of the object ('sidereal' or 'planetary').
     * @returns A promise that resolves when details are fetched.
     */
    async select(id: string, type: 'sidereal' | 'planetary') {
        // Reset if it's a new target to avoid showing old details
        if (this.targetId !== id) {
            this.targetDetails = null;
        }
        
        this.targetId = id;
        this.targetType = type;
        await this.fetchDetails(id, type);
    }

    /**
     * Fetches details for the specified object from the Sideris API.
     * 
     * @param id - The ID of the object.
     * @param type - The type of the object ('sidereal' or 'planetary').
     * @returns A promise that resolves when the fetch is complete.
     */
    private async fetchDetails(id: string, type: 'sidereal' | 'planetary') {
        if (this.isLoadingDetails) return;
        
        const activeLoc = locStore.active;
        if (!activeLoc) return;

        this.isLoadingDetails = true;
        try {
            const params = {
                target_time: timeEngine.current.toISOString(),
                lat: activeLoc.lat,
                lon: activeLoc.lng,
                elev: activeLoc.elevation
            };

            const details = await siderisAPI.getObjectDetails(type, id, params, getLocale());
            this.targetDetails = details;
            this.lastFetchTime = timeEngine.current.getTime();
        } catch (error) {
            console.error(`Failed to fetch details for ${id}:`, error);
        } finally {
            this.isLoadingDetails = false;
        }
    }

    /**
     * Clears the current selection and resets the store.
     */
    clear() {
        this.targetId = null;
        this.targetType = null;
        this.targetDetails = null;
        this.isLoadingDetails = false;
        this.lastFetchTime = 0;
    }
}

/**
 * Singleton instance of ActiveSelection.
 */
export const selectionStore = new ActiveSelection();
