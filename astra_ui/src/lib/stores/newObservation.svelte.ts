// src/lib/stores/newObservation.svelte.ts
class newObservationStore {
    showNewObsModal = $state(false);

    open() {
        this.showNewObsModal = true;
    }

    close() {
        this.showNewObsModal = false;
    }
}

export const newObsStore = new newObservationStore();