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