import { authAPI } from '$lib/api/auth';
import { browser } from '$app/environment';
import type { User } from '$lib/types/user';

class AuthStore {
    user = $state<User | null>(null);
    isLoading = $state(true);

    async init() {
        if (!browser) return;
        
        const token = localStorage.getItem('auth');
        if (token) {
            await this.refreshProfile();
        }
        this.isLoading = false;
    }

    async refreshProfile() {
        try {
            this.user = await authAPI.getUser();
        } catch (e) {
            this.logout();
        }
    }

    async login(token: string) {
        this.isLoading = true;
        try {
            await authAPI.login(token);
            await this.refreshProfile();
        } finally {
            this.isLoading = false;
        }
    }

    async logout() {
        await authAPI.logout();
        this.user = null;
    }

    isAuthenticated = $derived(this.user !== null);
}

export const authStore = new AuthStore();