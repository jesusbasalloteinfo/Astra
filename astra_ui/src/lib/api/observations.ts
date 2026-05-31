// src/lib/api/observations.ts
import { api } from './client';
import { endpoints } from './endpoints';
import type { Observation, ObservationCreate, ObservationUpdate } from '../types/observation';

/**
 * Observation API module for managing astronomical observation logs.
 */
export const observationAPI = {
    /**
     * Retrieves all observation logs for the current user.
     * @returns {Promise<Observation[]>} A list of observations.
     */
    list: async (): Promise<Observation[]> => {
        const response = await api.get<Observation[]>(endpoints.observations.base);
        return response.data;
    },

    /**
     * Retrieves a specific observation log by its ID.
     * @param {string} id - The unique identifier of the observation.
     * @returns {Promise<Observation>} The observation details.
     */
    get: async (id: string): Promise<Observation> => {
        const response = await api.get<Observation>(endpoints.observations.detail(id));
        return response.data;
    },

    /**
     * Creates a new observation log.
     * @param {ObservationCreate} data - The data for the new observation.
     * @returns {Promise<{ id: string }>} The ID of the newly created observation.
     */
    create: async (data: ObservationCreate): Promise<{ id: string }> => {
        const response = await api.post(endpoints.observations.base, data);
        return response.data;
    },

    /**
     * Updates an existing observation log.
     * @param {string} id - The unique identifier of the observation to update.
     * @param {ObservationUpdate} data - The updated observation data.
     * @returns {Promise<boolean>} True if the update was successful.
     */
    update: async (id: string, data: ObservationUpdate): Promise<boolean> => {
        const response = await api.patch(endpoints.observations.detail(id), data);
        return response.data.success;
    },

    /**
     * Deletes an observation log.
     * @param {string} id - The unique identifier of the observation to delete.
     * @returns {Promise<void>}
     */
    delete: async (id: string): Promise<void> => {
        await api.delete(endpoints.observations.detail(id));
    }
};