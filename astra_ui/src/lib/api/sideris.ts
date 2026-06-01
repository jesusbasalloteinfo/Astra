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

// src/lib/api/sideris.ts
import { api } from './client'; 
import { siderisEndpoints } from './endpoints';

/**
 * Parameters for synchronizing astronomical object positions with a specific observer context.
 */
export interface SyncParams {
    /** The target date and time in ISO format. */
    target_time: string;
    /** Observer's latitude in degrees. */
    lat: number;
    /** Observer's longitude in degrees. */
    lon: number;
    /** Observer's elevation in meters. */
    elev: number;
}

/**
 * Sideris API module for astronomical calculations, catalog lookups, and ephemeris data.
 */
export const siderisAPI = {
    /**
     * Synchronizes the positions of sidereal or planetary objects based on observer context.
     * @param {'sidereal' | 'planetary'} type - The catalog type to synchronize.
     * @param {SyncParams} params - The observer's location and target time.
     * @returns {Promise<any>} The synchronized position data.
     */
    async syncSky(type: 'sidereal' | 'planetary', params: SyncParams) {
        const url = type === 'sidereal' 
            ? siderisEndpoints.sidereal.sync 
            : siderisEndpoints.planetary.sync;

        const { data } = await api.get(url, { params });
        return data;
    },

    /**
     * Retrieves constellations metadata.
     * @param {string} [lang='en'] - The preferred language for metadata.
     * @returns {Promise<any>} Constellation information.
     */
    async getConstellations(lang: string = 'en') {
        const { data } = await api.get(siderisEndpoints.sidereal.constellations, {params: { lang } });
        return data;
    },

    /**
     * Retrieves metadata for sidereal or planetary objects.
     * Sidereal metadata is generally static, while planetary metadata requires observer context.
     * @param {'sidereal' | 'planetary'} type - The catalog type.
     * @param {SyncParams} [params] - Optional observer context (required for planetary).
     * @param {string} [lang='en'] - The preferred language for metadata.
     * @returns {Promise<any>} The object metadata.
     */
    async getMetadata(type: 'sidereal' | 'planetary', params?: SyncParams, lang: string = 'en') {
        const url = type === 'sidereal'
            ? siderisEndpoints.sidereal.metadata
            : siderisEndpoints.planetary.metadata;

        // Pasamos params solo si existen (para planetary)
        const { data } = await api.get(url, { params: { ...params, lang } });
        return data;
    },

    /**
     * Retrieves detailed ephemeris information for a specific astronomical object.
     * @param {'sidereal' | 'planetary'} type - The catalog type.
     * @param {string} id - The unique identifier of the object.
     * @param {SyncParams} params - The observer's location and target time.
     * @param {string} [lang='en'] - The preferred language for details.
     * @returns {Promise<any>} Detailed ephemeris data for the object.
     */
    async getObjectDetails(type: 'sidereal' | 'planetary', id: string, params: SyncParams, lang: string = 'en') {
        const url = type === 'sidereal'
            ? siderisEndpoints.sidereal.object(id)
            : siderisEndpoints.planetary.object(id);

        const { data } = await api.get(url, { params: { ...params, lang } });
        return data;
    }
};