import { api } from './client';
import { endpoints } from './endpoints';

export const authAPI = {
    login: async (token: string): Promise<void> => {
        await api.post(endpoints.auth.login, { token });
    },

    logout: async (): Promise<void> => {
        await api.post(endpoints.auth.logout);
    },

    session: async (): Promise<boolean> => {
        try {
            await api.get(endpoints.auth.session);
            return true;
        } catch {
            return false;
        }
    }
};