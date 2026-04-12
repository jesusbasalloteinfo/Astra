// lib/api/auth.ts
import { api } from './client';
import { endpoints } from './endpoints';
import { browser } from '$app/environment';
import type { User } from '$lib/types/user';

export const authAPI = {
    login: async (token: string): Promise<void> => {
        const response = await api.post(endpoints.auth.login, { token:token });
        
        if (browser && response.data.access_token) {
            localStorage.setItem('auth', response.data.access_token);
        }
    },

    logout: async (): Promise<void> => {
        try {
            await api.post(endpoints.auth.logout);
        } finally {
            if (browser) {
                localStorage.removeItem('auth');
            }
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

};

