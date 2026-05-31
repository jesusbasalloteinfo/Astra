import { observationAPI } from '$lib/api/observations';
import type { Observation, ObservationCreate, ObservationUpdate } from '$lib/types/observation';
import { authStore } from './auth.svelte';

/**
 * Store for managing the list of observation sessions.
 * Handles loading, creating, updating, and deleting observations.
 */
class ObservationStore {
    /** List of all observation sessions. */
    items = $state<Observation[]>([]);
    /** ID of the currently selected observation. */
    selectedId = $state<string | null>(null);
    /** Indicates if the store is loading observations. */
    isLoading = $state(false);

    /** Computed property that returns the currently selected observation object. */
    selected = $derived(
        this.items.find(i => i.id === this.selectedId) ?? null
    );
    
    /** Computed property that returns the total count of observations. */
    count = $derived(this.items.length);
    
    /**
     * Sorts observations by creation date in descending order.
     */
    private sortItems() {
        this.items.sort((a, b) => 
            new Date(b.creation).getTime() - new Date(a.creation).getTime()
        );
    }

    /**
     * Loads all observations for the authenticated user from the API.
     * 
     * @returns A promise that resolves when the observations are loaded.
     */
    async load() {
        // Loads the store with the API response and coordinates the store
        if (!authStore.isAuthenticated) return;

        this.isLoading = true;
        try {
            this.items = await observationAPI.list();
            this.sortItems();
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Creates a new observation session.
     * 
     * @param data - The data for the new observation.
     * @returns A promise that resolves with the ID of the newly created observation.
     */
    async create(data: ObservationCreate) {
        // Creates a new observation and updates the store
        const currentUser = authStore.user?.username;
        if (!currentUser) throw new Error("Not authenticated");

        try {
            const { id } = await observationAPI.create(data);

            const newObs: Observation = {
                id,
                name: data.name,
                description: data.description ?? '',
                owner: currentUser,
                creation: new Date().toISOString(),
                last_used: new Date().toISOString(),
            };

            this.items.unshift(newObs); // Add as most recent
            return id;
        } catch (error) {
            console.error("Error creating observation:", error);
            throw error;
        }
    }

    /**
     * Updates an existing observation session.
     * 
     * @param id - The ID of the observation to update.
     * @param data - The updated data.
     * @returns A promise that resolves when the update is complete.
     */
    async update(id: string, data: ObservationUpdate) {
        // Updates a concrete observation and does an optimistic observation update
        const success = await observationAPI.update(id, data);
        if (success) {
            this.items = this.items.map(item => 
                item.id === id ? { ...item, ...data } : item
            );
        }
    }

    /**
     * Deletes an observation session.
     * 
     * @param id - The ID of the observation to delete.
     * @returns A promise that resolves when the deletion is complete.
     */
    async remove(id: string) {
        // Deletes an observation from the DB and from the store
        await observationAPI.delete(id);
        this.items = this.items.filter(i => i.id !== id);
        if (this.selectedId === id) this.selectedId = null;
    }

    /**
     * Selects an observation session.
     * 
     * @param id - The ID of the observation to select, or null to deselect.
     */
    select(id: string | null) {
        // Selects a concrete observation
        this.selectedId = id;
    }

    /**
     * Resets the store to its initial state.
     */
    reset() {
        this.items = [];
        this.selectedId = null;
        this.isLoading = false;
    }

}

/**
 * Singleton instance of ObservationStore.
 */
export const obsStore = new ObservationStore();