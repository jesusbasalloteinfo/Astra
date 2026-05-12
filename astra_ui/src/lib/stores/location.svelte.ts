// src/lib/stores/location.svelte.ts
import { authStore } from './auth.svelte';
import { userAPI } from '$lib/api/user';
import type { LocationCreate } from '$lib/types/user';
import { browser } from '$app/environment';

class LocationStore {
    activeId = $state<string | null>(browser ? localStorage.getItem('active_location_id') : null);

    isSyncing = $state(false);
    isDetecting = $state(false);
    isAdding = $state(false); // UI control

    
    all = $derived(authStore.user?.locations || []);
    
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

    showForm() { this.isAdding = true; }
    hideForm() { this.isAdding = false; }

    get effectiveActiveId() {
        return this.active?.id || null;
    }

    select(id: string | null) {
        this.activeId = id;
        if (browser) {
            if (id) localStorage.setItem('active_location_id', id);
            else localStorage.removeItem('active_location_id');
        }
    }

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
                { timeout: 10000 }
            );
        });
    }

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

    clear() {
        this.activeId = null;
        if (browser) {
            localStorage.removeItem('active_location_id');
        }
    }
}

export const locStore = new LocationStore();