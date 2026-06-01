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

// lib/api/user.ts
import { api } from './client';
import { endpoints } from './endpoints';
import type { User, LocationCreate } from '$lib/types/user';

/**
 * User API module for managing user-specific data like locations.
 */
export const userAPI = {
    /**
     * Adds a new geographic location to the user's profile.
     * @param {LocationCreate} location - The location data to add.
     * @returns {Promise<void>}
     */
    addLocation: async (location: LocationCreate): Promise<void> => {
        const response = await api.post(endpoints.user.locations, location );  
        return response.data
    },

    /**
     * Removes a geographic location from the user's profile.
     * @param {string} id - The unique identifier of the location to remove.
     * @returns {Promise<void>}
     */
    removeLocation: async (id: string): Promise<void> => {
        const response = await api.delete(endpoints.user.location_get(id));  
        return response.data
    }
};
