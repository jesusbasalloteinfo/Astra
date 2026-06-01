/*
 * ASTRA - Automated Smart Telescope Remote Assistant
 * Copyright (C) 2026 Jesus Basallote
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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
