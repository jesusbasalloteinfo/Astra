import { authAPI } from '$lib/api/auth';
import { browser } from '$app/environment';
import type { User } from '$lib/types/user';
import { deviceStore } from './devices.svelte';
import { locStore } from './location.svelte';
import { obsStore } from './observations.svelte';
import { themeState } from '$lib/themes/themes.svelte';
import { getLocale, setLocale } from '$lib/paraglide/runtime.js';

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
            
            // Sync settings to local state
            if (this.user?.settings) {
                if (this.user.settings.theme && this.user.settings.theme !== themeState.current) {
                    themeState.set(this.user.settings.theme as any);
                }

                if (this.user.settings.language) {
                    // 1. Manually sync the cookie so the server knows for the next request
                    if (browser) {
                        document.cookie = `PARAGLIDE_LOCALE=${this.user.settings.language}; path=/; max-age=31536000; SameSite=Lax`;
                    }

                    // 2. Only call setLocale if it actually changed to avoid unnecessary reloads
                    if (this.user.settings.language !== getLocale()) {
                        setLocale(this.user.settings.language as any);
                    }
                }
            }
        } catch (e) {
            this.logout();
        }
    }

    async updateSettings(settings: { theme?: string; language?: string }) {
        if (!this.isAuthenticated) return;
        try {
            await authAPI.updateSettings(settings);
            if (this.user) {
                this.user.settings = { ...this.user.settings, ...settings };
                
                // If language changed, sync the cookie for the next page reload
                if (settings.language && browser) {
                    document.cookie = `PARAGLIDE_LOCALE=${settings.language}; path=/; max-age=31536000; SameSite=Lax`;
                }
            }
        } catch (e) {
            console.error("Failed to update settings:", e);
        }
    }

    async login(username: string, password: string, syncSettings = false) {
        this.isLoading = true;
        try {
            // Capture current local settings before they might be overwritten by refreshProfile
            const localTheme = themeState.current;
            const localLang = getLocale();

            await authAPI.login(username, password);
            
            if (syncSettings) {
                await authAPI.updateSettings({
                    theme: localTheme,
                    language: localLang
                });
            }

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