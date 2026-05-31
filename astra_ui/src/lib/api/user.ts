// lib/api/auth.ts
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
