import { browser } from '$app/environment';

export type ThemeId = 'standard' | 'dark' | 'light' | 'astronomical';

export interface Theme {
    id: ThemeId;
    label: string;
    icon: string;
}

export const THEMES: Theme[] = [
    { id: 'standard',     label: 'Standard',     icon: '⚪' },
    { id: 'dark',         label: 'Dark',          icon: '🌑' },
    { id: 'light',        label: 'Light',         icon: '☀️' },
    { id: 'astronomical', label: 'Astronomical',  icon: '🔴' },
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
            }
        }
    };
}

export const themeState = createThemeState();