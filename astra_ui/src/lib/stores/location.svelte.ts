// src/lib/stores/location.svelte.ts
import { authStore } from './auth.svelte';
import { userAPI } from '$lib/api/user';
import type { LocationCreate } from '$lib/types/user';
import { browser } from '$app/environment';

/**
 * Store for managing user locations.
 * Handles location selection, GPS detection, and adding/deleting locations.
 */
class LocationStore {
    /** ID of the currently active location. */
    activeId = $state<string | null>(browser ? localStorage.getItem('active_location_id') : null);

    /** Indicates if the store is syncing with the server. */
    isSyncing = $state(false);
    /** Indicates if GPS detection is in progress. */
    isDetecting = $state(false);
    /** Indicates if the add location form is visible. */
    isAdding = $state(false); // UI control

    /** Computed property that returns all available locations for the user. */
    all = $derived(authStore.user?.locations || []);
    
    /** Computed property that returns the effective active location object. */
    active = $derived.by(() => {
        if (this.all.length === 0) return null;

        // Manually selected
        const manual = this.all.find(l => l.id === this.activeId);
        if (manual) return manual;

        // Server saved
        const serverDefault = this.all.find(l => l.is_default);
        if (serverDefault) return serverDefault;

        // First one
        return this.all[0];
    });

    /** Shows the add location form. */
    showForm() { this.isAdding = true; }
    /** Hides the add location form. */
    hideForm() { this.isAdding = false; }

    /** Returns the ID of the effective active location. */
    get effectiveActiveId() {
        return this.active?.id || null;
    }

    /**
     * Selects a location as the active one.
     * 
     * @param id - The ID of the location to select, or null to deselect.
     */
    select(id: string | null) {
        this.activeId = id;
        if (browser) {
            if (id) localStorage.setItem('active_location_id', id);
            else localStorage.removeItem('active_location_id');
        }
    }

    /**
     * Detects the user's current GPS position.
     * 
     * @returns A promise that resolves with the detected location coordinates.
     */
    async detectGPS(): Promise<Partial<LocationCreate>> {
        this.isDetecting = true;
        
        return new Promise((resolve, reject) => {
            if (!browser || !navigator.geolocation) {
                this.isDetecting = false;
                return reject('GPS_NOT_SUPPORTED');
            }
            
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const tzOffsetHours = -(new Date().getTimezoneOffset() / 60);
                    this.isDetecting = false; 
                    resolve({
                        lat: pos.coords.latitude,
                        lng: pos.coords.longitude,
                        elevation: Math.round(pos.coords.altitude || 0),
                        timezone: tzOffsetHours || 0
                    });
                },
                (err) => {
                    this.isDetecting = false;
                    reject(err);
                },
                { 
                    enableHighAccuracy: true,
                    timeout: 30000,
                    maximumAge: 60000 
                }
            );
        });
    }

    /**
     * Adds a new location to the user's profile.
     * 
     * @param data - The location data to add.
     * @returns A promise that resolves when the location is added.
     */
    async addLocation(data: LocationCreate) {
        if (data.lat < -90 || data.lat > 90) throw new Error("Invalid latitude");
        if (data.lng < -180 || data.lng > 180) throw new Error("Invalid longitude");
        if (!data.label.trim()) throw new Error("Label is required");
        if (data.timezone < -12 || data.timezone > 14) {
            throw new Error("Invalid timezone offset");
        }

        this.isSyncing = true;

        try {
            await userAPI.addLocation(data);

            await authStore.refreshProfile();
            if (data.is_default) {
                this.select(null); 
            } 
            else if (this.all.length === 1) {
                this.select(this.all[0].id);
            }
            if (this.all.length === 1) this.activeId = this.all[0].id;
            this.hideForm();
        } finally {
            this.isSyncing = false;
        }
    }

    /**
     * Deletes a location from the user's profile.
     * 
     * @param id - The ID of the location to delete.
     * @returns A promise that resolves when the location is deleted.
     */
    async deleteLocation(id: string) {
        this.isSyncing = true;
        try {
            await userAPI.removeLocation(id);
            await authStore.refreshProfile();
            if (this.activeId === id) {
                this.select(null);
            }
        } finally {
            this.isSyncing = false;
        }
    }

    /**
     * Clears the active location and resets the store.
     */
    clear() {
        this.activeId = null;
        if (browser) {
            localStorage.removeItem('active_location_id');
        }
    }
}

/**
 * Singleton instance of LocationStore.
 */
export const locStore = new LocationStore();