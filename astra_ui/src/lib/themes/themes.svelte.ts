/*
 * ASTRA - Automated Smart Telescope Remote Assistant
 * Copyright (C) 2026 Jesus Basallote
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { browser } from '$app/environment';
import { Monitor, Moon, Sun, Telescope } from 'lucide-svelte';
import { authStore } from '$lib/stores/auth.svelte';


export type ThemeId = 'standard' | 'dark' | 'light' | 'astronomical';

export interface Theme {
    id: ThemeId;
    label: string;
    icon: any;
}
export const THEMES: Theme[] = [
    { id: 'standard',     label: 'Standard',     icon: Monitor },
    { id: 'dark',         label: 'Dark',          icon: Moon },
    { id: 'light',        label: 'Light',         icon: Sun },
    { id: 'astronomical', label: 'Astronomical',  icon: Telescope }, 
];

const STORAGE_KEY = 'theme';
const DEFAULT_THEME: ThemeId = 'standard';
const VALID: ThemeId[] = ['standard', 'dark', 'light', 'astronomical'];

function createThemeState() {
    let currentId = $state<ThemeId>(
        browser
            ? (VALID.includes(localStorage.getItem(STORAGE_KEY) as ThemeId)
                ? localStorage.getItem(STORAGE_KEY) as ThemeId
                : DEFAULT_THEME)
            : DEFAULT_THEME
    );

    return {
        get current() { return currentId; },
        set: (theme: ThemeId) => {
            currentId = theme;
            if (browser) {
                localStorage.setItem(STORAGE_KEY, theme);
                document.documentElement.setAttribute('data-theme', theme);

                // Persist to backend if logged in
                if (authStore.isAuthenticated && authStore.user?.settings.theme !== theme) {
                    authStore.updateSettings({ theme });
                }
            }
        }
    };
}

export const themeState = createThemeState();