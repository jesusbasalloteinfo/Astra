// lib/api/auth.ts
import { api } from './client';
import { endpoints } from './endpoints';
import { browser } from '$app/environment';
import type { User } from '$lib/types/user';

export const authAPI = {
    login: async (username: string, password: string): Promise<void> => {
        const response = await api.post(endpoints.auth.login, { username, password });
        
        if (browser && response.data.access_token) {
            localStorage.setItem('auth', response.data.access_token);
        }
    },

    register: async (username: string, email: string, password: string): Promise<void> => {
        await api.post(endpoints.auth.register, { username, email, password });
    },

    logout: async (): Promise<void> => {
        // Since we use JWT, logout is primarily local removal, 
        if (browser) {
            localStorage.removeItem('auth');
        }
    },

    session: async (): Promise<boolean> => {
        try {
            await api.get(endpoints.auth.session);
            return true;
        } catch {
            return false;
        }
    },

    getUser: async (): Promise<User> => {
        const response = await api.get(endpoints.auth.user_details);
        return response.data;
    },

    updateProfile: async (data: { full_name?: string; bio?: string }): Promise<void> => {
        await api.put(endpoints.user.update, data);
    },

    uploadProfilePicture: async (file: File): Promise<string> => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post(endpoints.auth.upload_picture, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data.url;
    }
};

