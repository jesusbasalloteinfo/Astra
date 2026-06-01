<!--
  ASTRA - Automated Smart Telescope Remote Assistant
  Copyright (C) 2026 Jesus Basallote
  
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.
  
  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<!-- src/lib/components/dashboard/MobileLanguageSelector.svelte -->
<script lang="ts">
	import { getLocale, setLocale } from '$lib/paraglide/runtime.js';
	import { page } from '$app/state';
    import { browser } from '$app/environment';
    import { authStore } from '$lib/stores/auth.svelte';
	import { AVAILABLE_LANGUAGES, type LanguageCode } from '$lib/config/languages';

    /** Current active locale code */
	let currentLocale = $state(getLocale()); 

    /**
     * Switches the application locale and reloads the page
     * @param {LanguageCode} newLocale - The locale code to switch to
     */
	async function switchLocale(newLocale: LanguageCode) {
		if (newLocale === currentLocale) return;

        // 1. Persist to backend if logged in and wait for it
        if (authStore.isAuthenticated && authStore.user?.settings.language !== newLocale) {
            await authStore.updateSettings({ language: newLocale });
        }

        // 2. Update local state and cookie
		setLocale(newLocale);
        if (browser) {
            document.cookie = `PARAGLIDE_LOCALE=${newLocale}; path=/; max-age=31536000; SameSite=Lax`;
        }
        currentLocale = newLocale;

		const segments = page.url.pathname.split('/');
		const supportedCodes = AVAILABLE_LANGUAGES.map(l => l.code);
		
        if (supportedCodes.includes(segments[1] as LanguageCode)) {
			segments[1] = newLocale;
			const newPath = segments.join('/') + page.url.search;
			window.location.replace(newPath);
		} else {
			window.location.reload();
		}
	}
</script>

<div class="flex flex-col gap-3">
    <span class="text-[10px] font-bold text-copy-muted uppercase tracking-[0.2em] px-1">Language</span>
    <div class="grid grid-cols-3 gap-2">
        {#each AVAILABLE_LANGUAGES as { code, label, svg }}
            {@const isActive = currentLocale === code}
            <button
                onclick={() => switchLocale(code)}
                class="flex flex-col items-center justify-center gap-2 p-3 rounded-2xl border transition-all active:scale-95
                       {isActive 
                        ? 'bg-accent/10 border-accent text-accent shadow-lg shadow-accent/5' 
                        : 'bg-surface border-border text-copy-secondary'}"
            >
                <div class="w-8 h-6 overflow-hidden rounded-md shadow-sm border border-white/10 [&>svg]:w-full [&>svg]:h-full [&>svg]:object-cover">
                    {@html svg}
                </div>
                <span class="text-[10px] font-black uppercase tracking-widest">{code}</span>
            </button>
        {/each}
    </div>
</div>
