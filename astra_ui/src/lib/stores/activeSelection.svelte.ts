// src/lib/stores/activeSelection.svelte.ts
import { siderisAPI } from '$lib/api/sideris';
import type { SiderealObjectDetails, PlanetaryObjectDetails } from '$lib/types/sideris';
import { locStore } from './location.svelte';
import { timeEngine } from './timeEngine.svelte';
import { getLocale } from '$lib/paraglide/runtime';

class ActiveSelection {
    targetId = $state<string | null>(null);
    targetType = $state<'sidereal' | 'planetary' | null>(null);
    targetDetails = $state<SiderealObjectDetails | PlanetaryObjectDetails | null>(null);
    isLoadingDetails = $state(false);

    private lastFetchTime: number = 0;

    constructor() {
        if (typeof window !== 'undefined') {
            $effect.root(() => {
                $effect(() => {
                    // Reactive dependency on time and ID
                    const id = this.targetId;
                    const type = this.targetType;
                    const currentTime = timeEngine.current;
                    
                    if (!id || !type) return;

                    // If time has drifted more than 5 minutes since last fetch, update details
                    // Also updates if we change target
                    const currentMs = currentTime.getTime();
                    const deltaMs = Math.abs(currentMs - this.lastFetchTime);
                    
                    if (deltaMs > 5 * 60 * 1000) {
                        this.fetchDetails(id, type);
                    }
                });
            });
        }
    }

    async select(id: string, type: 'sidereal' | 'planetary') {
        // Reset if it's a new target to avoid showing old details
        if (this.targetId !== id) {
            this.targetDetails = null;
        }
        
        this.targetId = id;
        this.targetType = type;
        await this.fetchDetails(id, type);
    }

    private async fetchDetails(id: string, type: 'sidereal' | 'planetary') {
        if (this.isLoadingDetails) return;
        
        const activeLoc = locStore.active;
        if (!activeLoc) return;

        this.isLoadingDetails = true;
        try {
            const params = {
                target_time: timeEngine.current.toISOString(),
                lat: activeLoc.lat,
                lon: activeLoc.lng,
                elev: activeLoc.elevation
            };

            const details = await siderisAPI.getObjectDetails(type, id, params, getLocale());
            this.targetDetails = details;
            this.lastFetchTime = timeEngine.current.getTime();
        } catch (error) {
            console.error(`Failed to fetch details for ${id}:`, error);
        } finally {
            this.isLoadingDetails = false;
        }
    }

    clear() {
        this.targetId = null;
        this.targetType = null;
        this.targetDetails = null;
        this.isLoadingDetails = false;
        this.lastFetchTime = 0;
    }
}

export const selectionStore = new ActiveSelection();
