// src/lib/stores/activeObservation.svelte.ts
import { obsStore } from './observations.svelte';
import type { Observation } from '$lib/types/observation';
import { observationAPI } from '$lib/api/observations';

class ActiveObservationStore {
    current = $state<Observation | null>(null);
    isLoading = $state(false);
    error = $state<string | null>(null);

    async setSession(id: string) {
        this.isLoading = true;
        this.error = null;

        try {
            // Search in observation storage
            let found = obsStore.items.find(o => o.id === id);

            if (found) {
                this.current = found;
            } else {
                // Load from API
                const data = await observationAPI.get(id); 
                this.current = data;
            }
        } catch (e) {
            console.error("Error loading active session:", e);
            this.error = "Could not synchronize with the observatory";
            this.current = null;
        } finally {
            this.isLoading = false;
        }
    }

    clear() {
        this.current = null;
        this.error = null;
    }
}

export const activeObs = new ActiveObservationStore(); 