import { observationAPI } from '$lib/api/observations';
import type { Observation, ObservationCreate, ObservationUpdate } from '$lib/types/observation';
import { authStore } from './auth.svelte';

class ObservationStore {
    // State runes
    items = $state<Observation[]>([]);
    selectedId = $state<string | null>(null);
    isLoading = $state(false);

    // Dependant states
    selected = $derived(
        this.items.find(i => i.id === this.selectedId) ?? null
    );
    
    count = $derived(this.items.length);
    
    private sortItems() {
        this.items.sort((a, b) => 
            new Date(b.creation).getTime() - new Date(a.creation).getTime()
        );
    }

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

    async update(id: string, data: ObservationUpdate) {
        // Updates a concrete observation and does an optimistic observation update
        const success = await observationAPI.update(id, data);
        if (success) {
            this.items = this.items.map(item => 
                item.id === id ? { ...item, ...data } : item
            );
        }
    }

    async remove(id: string) {
        // Deletes an observation from the DB and from the store
        await observationAPI.delete(id);
        this.items = this.items.filter(i => i.id !== id);
        if (this.selectedId === id) this.selectedId = null;
    }

    select(id: string | null) {
        // Selects a concrete observation
        this.selectedId = id;
    }

    reset() {
        this.items = [];
        this.selectedId = null;
        this.isLoading = false;
    }

}

export const obsStore = new ObservationStore();