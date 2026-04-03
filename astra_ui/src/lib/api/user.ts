// lib/api/auth.ts
import { api } from './client';
import { endpoints } from './endpoints';
import type { User, LocationCreate } from '$lib/types/user';

export const userAPI = {
    addLocation: async (location: LocationCreate): Promise<void> => {
        const response = await api.post(endpoints.user.locations, location );  
        return response.data
    },

    removeLocation: async (id: string): Promise<void> => {
        const response = await api.delete(endpoints.user.location_get(id));  
        return response.data
    }
};

