import { observationAPI } from '$lib/api/observations';
import type { Observation, ObservationCreate, ObservationUpdate } from '$lib/types/observation';
import { authStore } from './auth.svelte';

/**
 * Store for managing the list of observation sessions.
 * Handles loading, creating, updating, and deleting observations.
 */
class ObservationStore {
    /** Raw list of observation sessions. */
    private _items = $state<Observation[]>([]);
    /** List of all observation sessions, automatically sorted by last activity. */
    items = $derived(
        this._items.toSorted((a, b) => 
            new Date(b.last_used).getTime() - new Date(a.last_used).getTime()
        )
    );
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
     * Loads all observations for the authenticated user from the API.
     * 
     * @returns A promise that resolves when the observations are loaded.
     */
    async load() {
        // Loads the store with the API response and coordinates the store
        if (!authStore.isAuthenticated) return;

        this.isLoading = true;
        try {
            this._items = await observationAPI.list();
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Updates an item in the internal state.
     * Useful for synchronization from other stores.
     */
    updateItem(data: Observation) {
        const index = this._items.findIndex(o => o.id === data.id);
        if (index !== -1) {
            this._items[index] = data;
        } else {
            this._items.push(data);
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

            this._items.push(newObs); 
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
            this._items = this._items.map(item => 
                item.id === id ? { ...item, ...data, last_used: new Date().toISOString() } : item
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
        this._items = this._items.filter(i => i.id !== id);
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
        this._items = [];
        this.selectedId = null;
        this.isLoading = false;
    }

}

/**
 * Singleton instance of ObservationStore.
 */
export const obsStore = new ObservationStore();