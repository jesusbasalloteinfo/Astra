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

// lib/api/endpoints.ts
/**
 * Application API endpoints configuration.
 * Maps logical API modules to their respective URL paths.
 */
export const endpoints = {
    /** Base URL for all API requests, derived from environment variables or defaulting to '/api'. */
    apiBase: import.meta.env.VITE_API_URL ?? '/api',
    
    /** Authentication and session-related endpoints. */
    auth: {
        login:   'auth/login',
        register: 'auth/register',
        logout:  'auth/logout',
        session: 'auth/session',
        user_details: 'users/me',
        upload_picture: 'auth/me/picture'
    },
    
    /** User profile and settings endpoints. */
    user:{
        update: 'users/me',
        updateSettings: 'users/me/settings',
        locations: 'users/me/locations',
        /**
         * Returns the endpoint for a specific location.
         * @param {string} id - The location ID.
         * @returns {string} The formatted endpoint path.
         */
        location_get: (id: string) => `users/me/locations/${id}`,
    },
    
    /** Observation log endpoints. */
    observations: {
        base:   '/observations',
        /**
         * Returns the endpoint for a specific observation.
         * @param {string} id - The observation ID.
         * @returns {string} The formatted endpoint path.
         */
        detail: (id: string) => `/observations/${id}`,
    },
    
    /** Chat and AI assistant endpoints. */
    chat: {
        /**
         * Returns the endpoint for a chat session associated with an observation.
         * @param {string} observation_id - The observation ID.
         * @returns {string} The formatted endpoint path.
         */
        session: (observation_id: string) => `/chat/session/${observation_id}`,
        /**
         * Returns the endpoint for streaming chat responses.
         * @param {string} session_id - The chat session ID.
         * @returns {string} The formatted endpoint path.
         */
        stream: (session_id: string) => `/chat/stream/${session_id}`,
    },
    
    /** Device management and telescope control endpoints. */
    devices:{
        pairDevice: 'devices/pair',
        getDevices: 'devices',
        /**
         * Returns the endpoint for a specific device's information.
         * @param {string} id - The device ID.
         * @returns {string} The formatted endpoint path.
         */
        getDeviceInfo: (id: string) => `devices/${id}`,
        /**
         * Returns the endpoint for a specific telescope's position.
         * @param {string} id - The device ID.
         * @returns {string} The formatted endpoint path.
         */
        getTelescopePos: (id: string) => `devices/${id}/telescope/position`,
        /**
         * Returns the endpoint for slewing a specific telescope.
         * @param {string} id - The device ID.
         * @returns {string} The formatted endpoint path.
         */
        slewTelescope: (id: string) => `devices/${id}/telescope/slew`,
        /**
         * Returns the endpoint for aborting a specific telescope's motion.
         * @param {string} id - The device ID.
         * @returns {string} The formatted endpoint path.
         */
        abortTelescope: (id: string) => `devices/${id}/telescope/abort`,
    }
} as const;



/**
 * Sideris catalog service endpoints configuration.
 * Maps astronomical catalog modules to their respective URL paths.
 */
export const siderisEndpoints = {
    /** Base path for the Sideris service. */
    base: '/sideris',
    
    /** Sidereal (deep sky) catalog endpoints. */
    sidereal: {
        sync: '/sideris/sidereal/sync',
        constellations: '/sideris/sidereal/constellations',
        metadata: '/sideris/sidereal/metadata',
        /**
         * Returns the endpoint for a specific sidereal object.
         * @param {string} id - The object identifier.
         * @returns {string} The formatted endpoint path.
         */
        object: (id: string) => `/sideris/sidereal/${id}`
    },
    
    /** Planetary (solar system) catalog endpoints. */
    planetary: {
        sync: '/sideris/planetary/sync',
        metadata: '/sideris/planetary/metadata',
        /**
         * Returns the endpoint for a specific planetary object.
         * @param {string} id - The object identifier.
         * @returns {string} The formatted endpoint path.
         */
        object: (id: string) => `/sideris/planetary/${id}`
    }
} as const;
