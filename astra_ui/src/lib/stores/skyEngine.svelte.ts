// src/lib/stores/skyEngine.svelte.ts
import { siderisAPI } from '$lib/api/sideris';
import { timeEngine } from './timeEngine.svelte';
import { locStore } from './location.svelte';

/**
 * Data structure for linear interpolation of celestial object positions.
 */
interface InterpolationData {
    /** Starting Altitude (degrees) */
    baseAlt: number;
    /** Starting Azimuth (degrees) */
    baseAz: number;
    /** Altitude velocity (degrees per second) */
    dAlt: number;
    /** Azimuth velocity (degrees per second) */
    dAz: number;
}

/**
 * Map of object IDs to their calculated altitude and azimuth.
 */
export type PositionUpdates = Map<string, { alt: number, az: number }>

/**
 * SkyEngine handles the real-time calculation and synchronization of celestial object positions.
 * It uses linear interpolation (kinematics) between API syncs to provide smooth, high-frequency updates.
 */
class SkyEngine {

    // --- State & Cache ---
    /** Fast storage for sidereal object kinematics data. */
    private siderealSync = $state<Map<string, InterpolationData>>(new Map());
    /** Fast storage for planetary object kinematics data. */
    private planetarySync = $state<Map<string, InterpolationData>>(new Map());
    
    // Time tracking and lifecycle management
    /** Whether the engine is currently active and updating positions. */
    isRunning = $state(false);
    /** The simulation time (ms) of the last successful API synchronization. */
    private lastSyncTime = $state<number>(0);
    /** Time-To-Live for the current vectors in seconds. */
    private ttlSeconds = $state<number>(120);
    
    /** Whether an API synchronization is currently in progress. */
    isSyncing = $state(false);

    // --- REAL-TIME POSITIONS ---
    /**
     * Automatically recalculates all object positions for every clock tick, using the delta positions.
     * Derived from the current simulation time and cached interpolation data.
     */
    positions = $derived.by(() => {
        const results: PositionUpdates = new Map();
        if (this.lastSyncTime === 0) return results;

        // Time delta in seconds since the last API fetch
        let dt = (timeEngine.targetTime - this.lastSyncTime) / 1000;

        // Prevent wild distortion on large time jumps
        // If the user jumps far into the future/past, the sky will freeze at the TTL*45 (max 90m) edge until the new API sync completes.
        if (Math.abs(dt) > this.ttlSeconds*45) {
            dt = Math.sign(dt) * this.ttlSeconds;
        }

        /**
         * Helper function for linear interpolation
         * @param data The map of interpolation data to process
         */
        const interpolate = (data: Map<string, InterpolationData>) => {
            data.forEach((obj, id) => {
                let newAlt = obj.baseAlt + (obj.dAlt * dt);
                let newAz = obj.baseAz + (obj.dAz * dt);

                // Keep Azimuth between 0° and 360°
                newAz = (newAz % 360 + 360) % 360;

                results.set(id, {
                    alt: newAlt,
                    az: newAz
                });
            });
        };

        interpolate(this.siderealSync);
        interpolate(this.planetarySync);

        return results;
    });

    // --- AUTO-REFRESH LOGIC ---

    /**
     * Monitors if the vectors have reached the TTL and need synchronization.
     * Returns true if a new sync is required.
     */
    private needsSync = $derived.by(() => {
        if (!locStore.active) return false;
        if (this.lastSyncTime === 0) return true; // Initial boot
        
        // Time from last fetch
        const ageSeconds = Math.abs(timeEngine.targetTime - this.lastSyncTime) / 1000;

        // Gets ahead of the ttl by syncing at 90% of the TTL to mask network latency, to
        // ensure new data arrives before the old data expires.
        return ageSeconds >= (this.ttlSeconds * 0.9); 
    });

    /**
     * Initializes the SkyEngine and sets up reactive effects for location changes and auto-sync.
     */
    constructor() {
        // In Svelte 5, the store monitors its own reactivity in an isolated root.
        if (typeof window !== 'undefined') {
            $effect.root(() => {
                let lastLocId = locStore.active?.id;
                $effect(() => {
                    // User has changed location
                    if (locStore.active && locStore.active.id !== lastLocId) {
                        console.log("Location changed! Resetting physics engine...");
                        lastLocId = locStore.active.id;
                        this.reset(); 
                    }
                });

                $effect(() => {
                    // If the derived state signals a need for sync, and we aren't already fetching...
                    if (this.isRunning && this.needsSync && !this.isSyncing && locStore.active) {
                        this.performSync();
                    }
                });
            });
        }
    }

    /**
     * Fetches new Base Positions and Velocities from Sideris API.
     * Updates internal interpolation maps and establishes a new time baseline.
     */
    private async performSync() {
        this.isSyncing = true;
        const loc = locStore.active!;
        
        // We "freeze" the exact simulation time of this request. 
        // This acts as the T0 (Time Zero) for our kinematics math when the response arrives.
        const captureTime = timeEngine.targetTime; 
        const params = {
            target_time: timeEngine.current.toISOString(), // in UTC
            lat: loc.lat,
            lon: loc.lng,
            elev: loc.elevation
        };

        try {
            // Concurrent fetching for sidereal and planetary data
            const [siderealRes, planetaryRes] = await Promise.all([
                siderisAPI.syncSky('sidereal', params),
                siderisAPI.syncSky('planetary', params)
            ]);

            this.ttlSeconds = siderealRes.ttl;
            
            // Repopulate interpolation maps with fresh vectors
            this.siderealSync.clear();
            siderealRes.updates.forEach(([id, alt, az, dAlt, dAz]: any) => {
                this.siderealSync.set(id, { baseAlt: alt, baseAz: az, dAlt, dAz });
            });

            this.planetarySync.clear();
            planetaryRes.updates.forEach(([id, alt, az, dAlt, dAz]: any) => {
                this.planetarySync.set(id, { baseAlt: alt, baseAz: az, dAlt, dAz });
            });

            // Commit the sync and establish the new time baseline
            this.lastSyncTime = captureTime;

        } catch (e) {
            console.error("Error in SkyEngine Sync:", e);
        } finally {
            this.isSyncing = false;
        }
    }

    /**
     * Clears physical data cache and resets the synchronization timer.
     */
    reset() {
        this.siderealSync.clear();
        this.planetarySync.clear();
        this.lastSyncTime = 0;
    }
}

/**
 * Singleton instance of the SkyEngine.
 */
export const skyEngine = new SkyEngine();