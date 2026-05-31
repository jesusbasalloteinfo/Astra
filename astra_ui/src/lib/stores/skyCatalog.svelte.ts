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

/**
 * Represents a single search result from the celestial catalog.
 */
export interface SearchResult {
    id: string;
    name: string;
    type: string;
    mag: number | null;
}

/**
 * Store for managing the celestial object catalog.
 * Handles sidereal, planetary, and constellation metadata, and providing search functionality.
 */
class CatalogStore {
    
    /** Dictionary of sidereal object metadata indexed by ID. */
    siderealData = $state<Record<string, SiderealObjectMetadata>>({});
    /** Dictionary of planetary object metadata indexed by ID. */
    planetaryData = $state<Record<string, PlanetaryObjectMetadata>>({});
    
    /** List of all constellations. */
    constellations = $state<ConstellationMetadata[]>([]);
    
    /** Indicates if the catalog has been fully loaded. */
    isLoaded = $state(false);
    /** Indicates if the catalog is currently loading. */
    isLoading = $state(false);
    /** Indicates if the catalog manager is running and should react to location changes. */
    isRunning = $state(false);
    /** Error message if catalog synchronization fails. */
    error = $state<string | null>(null);

    /** Timestamp of the last planetary metadata update. */
    private lastPlanetaryUpdate = 0; 

    /** Internal index for fast object searching. */
    private searchIndex: { key: string, result: SearchResult }[] = [];

    /**
     * Initializes the store and sets up an effect to trigger initial catalog loading
     * when a location is active.
     */
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
     * Performs the initial full catalog fetch (Sidereal, Constellations, and Planetary).
     * 
     * @param params - Synchronization parameters (time, coordinates).
     * @returns A promise that resolves when the catalog is initialized.
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
     * Checks for planetary updates and refetches if significant time has passed.
     * 
     * @param params - Current synchronization parameters.
     * @returns A promise that resolves after the update check.
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
     * Creates a fast search dictionary by flattening all possible object names.
     */
    private buildSearchIndex() {
        this.searchIndex = [];

        for (const [id, data] of Object.entries(this.planetaryData)) {
            
            const displayName = data.name;
            
            const res = { id, name: displayName, type: data.type, category: data.category, mag: data.mag };

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
            const res = { id, name: displayName, type: data.type || 'sidereal', category: data.category || 'star', mag: data.mag };

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
            
            const res = { id: constel.abbr, name: constel.name, type: 'constellation', category: 'constellation', mag: null };

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
     * Searches for objects within the catalog based on a query string.
     * 
     * @param query - The search query.
     * @param limit - The maximum number of results to return.
     * @returns An array of SearchResult objects.
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

    /**
     * Retrieves metadata for a specific celestial object by its ID.
     * 
     * @param objId - The ID of the object.
     * @returns Metadata for the object, or null if not found.
     */
    getInfo(objId:string): SiderealObjectMetadata | PlanetaryObjectMetadata | null {
        if (objId in this.siderealData) return this.siderealData[objId];
        if (objId in this.planetaryData) return this.planetaryData[objId];
        return null;        
    }

    /**
     * Retrieves the name of a constellation by its abbreviation.
     * 
     * @param abbr - The constellation abbreviation (e.g., 'Ori').
     * @param latin - Whether to return the Latin name.
     * @returns The constellation name, or null if not found.
     */
    getConstellationName(abbr: string, latin:boolean=false): string | null {
        const constellation = this.constellations.find(c => c.abbr === abbr);
        return constellation && !latin ? constellation.name : latin && constellation?.latin ? constellation.latin : null;
    }


    /**
     * Clears the catalog data and resets the store to its initial state.
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

/**
 * Singleton instance of CatalogStore.
 */
export const catalogStore = new CatalogStore();