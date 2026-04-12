// src/lib/api/sideris.ts
import { api } from './client'; 
import { siderisEndpoints } from './endpoints';

export interface SyncParams {
    target_time: string;
    lat: number;
    lon: number;
    elev: number;
}

export const siderisAPI = {
    /**
     * Sync the sidereal or planetary positions
     */
    async syncSky(type: 'sidereal' | 'planetary', params: SyncParams) {
        const url = type === 'sidereal' 
            ? siderisEndpoints.sidereal.sync 
            : siderisEndpoints.planetary.sync;

        const { data } = await api.get(url, { params });
        return data;
    },

    /**
     * Get the constellations metadata
     */
    async getConstellations() {
        const { data } = await api.get(siderisEndpoints.sidereal.constellations);
        return data;
    },

    /**
     * Get metadata from sidereal or planetary objects
     * 
     * Sidereal is static, Planetary requires observer context.
     */
    async getMetadata(type: 'sidereal' | 'planetary', params?: SyncParams) {
        const url = type === 'sidereal'
            ? siderisEndpoints.sidereal.metadata
            : siderisEndpoints.planetary.metadata;

        // Pasamos params solo si existen (para planetary)
        const { data } = await api.get(url, { params });
        return data;
    },
    /**
     * Get an object's detailed ephemeris
     */
    async getObjectDetails(type: 'sidereal' | 'planetary', id: string, params: SyncParams) {
        const url = type === 'sidereal'
            ? siderisEndpoints.sidereal.object(id)
            : siderisEndpoints.planetary.object(id);

        const { data } = await api.get(url, { params });
        return data;
    }
};