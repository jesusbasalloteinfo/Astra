// lib/api/auth.ts
import { api } from './client';
import { endpoints } from './endpoints';
import { browser } from '$app/environment';
import type { User } from '$lib/types/user';

/**
 * Authentication API module for handling user login, registration, and session management.
 */
export const authAPI = {
    /**
     * Authenticates a user with username and password.
     * @param {string} username - The user's username.
     * @param {string} password - The user's password.
     * @returns {Promise<void>}
     */
    login: async (username: string, password: string): Promise<void> => {
        const response = await api.post(endpoints.auth.login, { username, password });
        
        if (browser && response.data.access_token) {
            localStorage.setItem('auth', response.data.access_token);
        }
    },

    /**
     * Registers a new user.
     * @param {string} username - The desired username.
     * @param {string} email - The user's email address.
     * @param {string} password - The user's password.
     * @returns {Promise<void>}
     */
    register: async (username: string, email: string, password: string): Promise<void> => {
        await api.post(endpoints.auth.register, { username, email, password });
    },

    /**
     * Logs out the current user by removing the authentication token.
     * @returns {Promise<void>}
     */
    logout: async (): Promise<void> => {
        // Since we use JWT, logout is primarily local removal, 
        if (browser) {
            localStorage.removeItem('auth');
        }
    },

    /**
     * Checks if the current session is valid.
     * @returns {Promise<boolean>} True if the session is valid, false otherwise.
     */
    session: async (): Promise<boolean> => {
        try {
            await api.get(endpoints.auth.session);
            return true;
        } catch {
            return false;
        }
    },

    /**
     * Retrieves the current user's profile information.
     * @returns {Promise<User>} The user profile data.
     */
    getUser: async (): Promise<User> => {
        const response = await api.get(endpoints.auth.user_details);
        return response.data;
    },

    /**
     * Updates the user's profile information.
     * @param {Object} data - The profile data to update.
     * @param {string} [data.full_name] - The user's full name.
     * @param {string} [data.bio] - The user's biography.
     * @returns {Promise<void>}
     */
    updateProfile: async (data: { full_name?: string; bio?: string }): Promise<void> => {
        await api.put(endpoints.user.update, data);
    },

    /**
     * Updates the user's application settings.
     * @param {Object} data - The settings to update.
     * @param {string} [data.theme] - The preferred UI theme.
     * @param {string} [data.language] - The preferred UI language.
     * @returns {Promise<void>}
     */
    updateSettings: async (data: { theme?: string; language?: string }): Promise<void> => {
        await api.put(endpoints.user.updateSettings, data);
    },

    /**
     * Uploads a new profile picture for the user.
     * @param {File} file - The image file to upload.
     * @returns {Promise<string>} The URL of the uploaded profile picture.
     */
    uploadProfilePicture: async (file: File): Promise<string> => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post(endpoints.auth.upload_picture, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data.url;
    }
};
