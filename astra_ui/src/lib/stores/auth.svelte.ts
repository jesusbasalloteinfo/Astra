import { authAPI } from '$lib/api/auth';
import { browser } from '$app/environment';
import type { User } from '$lib/types/user';
import { deviceStore } from './devices.svelte';
import { locStore } from './location.svelte';
import { obsStore } from './observations.svelte';
import { themeState } from '$lib/themes/themes.svelte';
import { getLocale, setLocale } from '$lib/paraglide/runtime.js';

/**
 * Store for managing user authentication and profile settings.
 */
class AuthStore {
    /** The currently authenticated user, or null if not logged in. */
    user = $state<User | null>(null);
    /** Loading state for authentication processes. */
    isLoading = $state(true);
    /** Indicates if a logout process is currently in progress. */
    isLoggingOut = $state(false);

    /**
     * Initializes the auth store by checking for an existing session in localStorage.
     * @returns A promise that resolves when initialization is complete.
     */
    async init() {
        if (!browser) return;
        
        const token = localStorage.getItem('auth');
        if (token) {
            await this.refreshProfile();
        }
        this.isLoading = false;
    }

    /**
     * Refreshes the user's profile and synchronizes settings like theme and language.
     * @returns A promise that resolves when the profile is refreshed.
     */
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

    /**
     * Updates the user's settings (theme, language) on the server and locally.
     * @param settings - The settings to update.
     * @returns A promise that resolves when the settings are updated.
     */
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

    /**
     * Logs the user in with the provided credentials.
     * 
     * @param username - The user's username.
     * @param password - The user's password.
     * @param syncSettings - Whether to sync local settings to the server after login.
     * @returns A promise that resolves when the login process is complete.
     */
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

    /**
     * Logs the user out, clears local data and resets related stores.
     * @returns A promise that resolves when the logout process is complete.
     */
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

    /**
     * Computed property that indicates if the user is currently authenticated.
     */
    isAuthenticated = $derived(this.user !== null);
}

/**
 * Singleton instance of AuthStore.
 */
export const authStore = new AuthStore();