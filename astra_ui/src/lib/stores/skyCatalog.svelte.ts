// src/lib/stores/skyCatalog.svelte.ts
import { siderisAPI } from '$lib/api/sideris';
import type { SyncParams } from '$lib/api/sideris';
import type { 
    SiderealObjectMetadata, 
    PlanetaryObjectMetadata, 
    ConstellationMetadata,
    SiderealCatalogResponse,
    PlanetaryCatalogResponse,
    ConstellationCatalogResponse
} from '$lib/types/sideris';
import { locStore } from './location.svelte';
import { timeEngine } from './timeEngine.svelte';
import { untrack } from 'svelte';


class CatalogStore {
    
    // Fast dictionary storage
    siderealData = $state<Record<string, SiderealObjectMetadata>>({});
    planetaryData = $state<Record<string, PlanetaryObjectMetadata>>({});
    
    constellations = $state<ConstellationMetadata[]>([]);
    
    // Store control flags
    isLoaded = $state(false);
    isLoading = $state(false);
    isRunning = $state(false);
    error = $state<string | null>(null);

    private lastPlanetaryUpdate = 0; 

    constructor() {
        // Effect root to manage auto-subscriptions safely outside a component
        if (typeof window !== 'undefined') { // Only browser
            $effect.root(() => {
                $effect(() => {
                    // If a location is active and the catalog is empty, trigger the initial load
                    if (this.isRunning && locStore.active && !this.isLoaded && !this.isLoading) {
                        
                        // untrack() to prevent this effect from re-running 60 times a second with every tick
                        // Just get the current time at init for the catalog fetching
                        const timeIso = untrack(() => timeEngine.current.toISOString());
                        
                        const params = {
                            target_time: timeIso,
                            lat: locStore.active.lat,
                            lon: locStore.active.lng,
                            elev: locStore.active.elevation
                        };
                        
                        this.init(params);
                    }
                });
            });
        }
    }

    /**
     * Initial full catalog fetch (Sidereal, Constellations, and Planetary)
     */
    async init(params: SyncParams) {
        if (this.isLoaded || this.isLoading) return;

        this.isLoading = true;
        this.error = null;

        try {
            // Execute all 3 requests concurrently
            const [siderealRes, constelRes, planetaryRes] = await Promise.all([
                siderisAPI.getMetadata('sidereal') as Promise<SiderealCatalogResponse>,
                siderisAPI.getConstellations() as Promise<ConstellationCatalogResponse>,
                siderisAPI.getMetadata('planetary', params) as Promise<PlanetaryCatalogResponse>
            ]);
            
            this.siderealData = siderealRes.data;
            this.constellations = constelRes.data;
            this.planetaryData = planetaryRes.data;
            
            this.lastPlanetaryUpdate = new Date(params.target_time).getTime();
            this.isLoaded = true;

        } catch (e) {
            console.error("Failed to initialize sky catalogs:", e);
            this.error = "Catalog synchronization failed.";
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Updates only planetary metadata if a significant amount of 
     * simulated time has passed or if time has made a major time change.
     */
    async checkUpdates(params: SyncParams) {
        if (!this.isLoaded) return;

        const targetMs = new Date(params.target_time).getTime();
        const deltaSec = Math.abs(targetMs - this.lastPlanetaryUpdate) / (1000);

        // Every 5 minuts, refetch the planetary metadata.
        if (deltaSec >= 300) {
            try {
                const res = await siderisAPI.getMetadata('planetary', params) as PlanetaryCatalogResponse;
                this.planetaryData = res.data;
                this.lastPlanetaryUpdate = targetMs;
            } catch (e) {
                console.error("Failed to update planetary metadata:", e);
            }
        }
    }

    getInfo(objId:string): SiderealObjectMetadata | PlanetaryObjectMetadata | null {
        if (objId in this.siderealData) return this.siderealData[objId];
        if (objId in this.planetaryData) return this.planetaryData[objId];
        return null;        
    }

    /**
     * Clears the cache and resets the store
     */
    reset() {
        this.siderealData = {};
        this.planetaryData = {};
        this.constellations = [];
        this.isLoaded = false;
        this.error = null;
        this.lastPlanetaryUpdate = 0;
    }
}

export const catalogStore = new CatalogStore();