// src/lib/stores/activeObservation.svelte.ts
import { obsStore } from './observations.svelte';
import type { Observation } from '$lib/types/observation';
import { observationAPI } from '$lib/api/observations';

/**
 * Store for managing the currently active observation session.
 */
class ActiveObservationStore {
    /** The current active observation, or null if none. */
    current = $state<Observation | null>(null);
    /** Loading state for the active observation. */
    isLoading = $state(false);
    /** Error message if loading fails. */
    error = $state<string | null>(null);

    /**
     * Sets the active observation session by ID.
     * Attempts to find the observation in the local store first, then falls back to the API.
     * 
     * @param id - The unique identifier of the observation session.
     * @returns A promise that resolves when the session is set.
     */
    async setSession(id: string) {
        this.isLoading = true;
        this.error = null;

        try {
            // Load from API
            const data = await observationAPI.get(id); 
            this.current = data;

            // Sync with local list store to trigger automatic re-sort
            obsStore.updateItem(data);
        } catch (e) {
            console.error("Error loading active session:", e);
            this.error = "Could not synchronize with the observatory";
            this.current = null;
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Clears the current active observation and resets errors.
     */
    clear() {
        this.current = null;
        this.error = null;
    }
}

/**
 * Singleton instance of ActiveObservationStore.
 */
export const activeObs = new ActiveObservationStore(); 
