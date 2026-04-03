// src/lib/api/observations.ts
import { api } from './client';
import { endpoints } from './endpoints';
import type { Observation, ObservationCreate, ObservationUpdate } from '../types/observation';

export const observationAPI = {
    // Get all user observations
    list: async (): Promise<Observation[]> => {
        const response = await api.get<Observation[]>(endpoints.observations.base);
        return response.data;
    },

    // Get an observation
    get: async (id: string): Promise<Observation> => {
        const response = await api.get<Observation>(endpoints.observations.detail(id));
        return response.data;
    },

    // Create observation
    create: async (data: ObservationCreate): Promise<{ id: string }> => {
        const response = await api.post(endpoints.observations.base, data);
        return response.data;
    },

    // Update observation
    update: async (id: string, data: ObservationUpdate): Promise<boolean> => {
        const response = await api.patch(endpoints.observations.detail(id), data);
        return response.data.success;
    },

    // Delete observation
    delete: async (id: string): Promise<void> => {
        await api.delete(endpoints.observations.detail(id));
    }
};