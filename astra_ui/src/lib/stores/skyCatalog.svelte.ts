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
import { getLocale } from '$lib/paraglide/runtime';

export interface SearchResult {
    id: string;
    name: string;
    type: string;
    mag: number | null;
}
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

    private searchIndex: { key: string, result: SearchResult }[] = [];

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
                siderisAPI.getMetadata('sidereal', undefined, getLocale()) as Promise<SiderealCatalogResponse>,
                siderisAPI.getConstellations(getLocale()) as Promise<ConstellationCatalogResponse>,
                siderisAPI.getMetadata('planetary', params, getLocale()) as Promise<PlanetaryCatalogResponse>
            ]);
            
            this.siderealData = siderealRes.data;
            this.constellations = constelRes.data;
            this.planetaryData = planetaryRes.data;

            this.buildSearchIndex();
            
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
                const res = await siderisAPI.getMetadata('planetary', params, getLocale()) as PlanetaryCatalogResponse;
                this.planetaryData = res.data;
                this.lastPlanetaryUpdate = targetMs;
                this.buildSearchIndex();
            } catch (e) {
                console.error("Failed to update planetary metadata:", e);
            }
        }
    }

    /**
     * Creates a fast search dictionary flattening all possible names
     */
    private buildSearchIndex() {
        this.searchIndex = [];

        for (const [id, data] of Object.entries(this.planetaryData)) {
            
            const displayName = data.name;
            
            const res = { id, name: displayName, type: data.type, mag: data.mag };

            const possibleNames = [
                data.name,
                ...(data.common_names || []),
                id
            ];

            for (const name of possibleNames) {
                if (name) {
                    const searchKey = name.toLowerCase().replace(/\s+/g, '');
                    this.searchIndex.push({ key: searchKey, result: res });
                }
            }
        }
        // Sidereal indexing
        for (const [id, data] of Object.entries(this.siderealData)) {
            const displayName = data.name || data.common_names?.[0] || data.catalog_names?.[0] || id;
            const res = { id, name: displayName, type: data.type || 'Star', mag: data.mag };

            const possibleNames = [
                data.name,
                ...(data.common_names || []),
                ...(data.catalog_names || []),
                id
            ];

            for (const name of possibleNames) {
                if (name) {
                    const searchKey = name.toLowerCase().replace(/\s+/g, '');
                    this.searchIndex.push({ key: searchKey, result: res });
                }
            }
        }
        // Constellation indexing
        for (const constel of this.constellations) {
            
            const res = { id: constel.abbr, name: constel.name, type: 'constellation', mag: null };

            const possibleNames = [
                constel.name,
                constel.latin,
                constel.abbr
            ];

            for (const name of possibleNames) {
                if (name) {
                    const searchKey = name.toLowerCase().replace(/\s+/g, '');
                    this.searchIndex.push({ key: searchKey, result: res });
                }
            }
        }
    }

    /**
     * Search objects within the catalog, normalising the search query
     */
    public searchObjects(query: string, limit = 10): SearchResult[] {
        const cleanQuery = query.toLowerCase().replace(/\s+/g, '');
        if (cleanQuery.length < 2) return [];

        // Save result and relevance score (minor best)
        const matches = new Map<string, { result: SearchResult, score: number }>();

        for (const item of this.searchIndex) {
            if (item.key.includes(cleanQuery)) {
                
                let score = 3; // Default coincidence
                if (item.key === cleanQuery) {
                    score = 1; // Exact coincidence
                } else if (item.key.startsWith(cleanQuery)) {
                    score = 2; // Starts with
                }

                if (!matches.has(item.result.id)) {
                    matches.set(item.result.id, { result: item.result, score });
                } else {
                    // If an object has multiple names, get the best score
                    const existing = matches.get(item.result.id)!;
                    if (score < existing.score) {
                        existing.score = score;
                    }
                }
            }
        }

        // Sort by Score and magnitude
        return Array.from(matches.values())
            .sort((a, b) => {
                if (a.score !== b.score) {
                    return a.score - b.score;
                }
                return (a.result.mag ?? 99) - (b.result.mag ?? 99);
            })
            .map(item => item.result)
            .slice(0, limit);
    }


    getInfo(objId:string): SiderealObjectMetadata | PlanetaryObjectMetadata | null {
        if (objId in this.siderealData) return this.siderealData[objId];
        if (objId in this.planetaryData) return this.planetaryData[objId];
        return null;        
    }

    /**
     * Get a constellation name or in latin with an id
     */
    getConstellationName(abbr: string, latin:boolean=false): string | null {
        const constellation = this.constellations.find(c => c.abbr === abbr);
        return constellation && !latin ? constellation.name : latin && constellation?.latin ? constellation.latin : null;
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