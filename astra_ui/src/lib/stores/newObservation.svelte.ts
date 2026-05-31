// src/lib/stores/newObservation.svelte.ts
/**
 * Store for managing the visibility of the new observation modal.
 */
class newObservationStore {
    /** Indicates if the new observation modal is visible. */
    showNewObsModal = $state(false);

    /**
     * Opens the new observation modal.
     */
    open() {
        this.showNewObsModal = true;
    }

    /**
     * Closes the new observation modal.
     */
    close() {
        this.showNewObsModal = false;
    }
}

/**
 * Singleton instance of newObservationStore.
 */
export const newObsStore = new newObservationStore();