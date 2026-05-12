import { authAPI } from '$lib/api/auth';
import { browser } from '$app/environment';
import type { User } from '$lib/types/user';
import { deviceStore } from './devices.svelte';
import { locStore } from './location.svelte';
import { obsStore } from './observations.svelte';

class AuthStore {
    user = $state<User | null>(null);
    isLoading = $state(true);
    isLoggingOut = $state(false);

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

    async login(username: string, password: string) {
        this.isLoading = true;
        try {
            await authAPI.login(username, password);
            await this.refreshProfile();
        } finally {
            this.isLoading = false;
        }
    }

    async logout() {
        this.isLoggingOut = true;
        try {
            await authAPI.logout();
        } finally {
            localStorage.removeItem('auth');
            this.user = null;
            this.isLoggingOut = false;
            deviceStore.clear();
            locStore.clear();
            obsStore.reset();
        }
    }

    isAuthenticated = $derived(this.user !== null);
}

export const authStore = new AuthStore();