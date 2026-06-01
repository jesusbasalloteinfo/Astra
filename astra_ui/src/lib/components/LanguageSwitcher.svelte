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

<script lang="ts">
	import { getLocale, setLocale } from '$lib/paraglide/runtime.js';
    import { browser } from '$app/environment';
	import { page } from '$app/state';
	import { fade } from 'svelte/transition';
	import { ChevronDown } from 'lucide-svelte';
    import { authStore } from '$lib/stores/auth.svelte';

	import { AVAILABLE_LANGUAGES, type LanguageCode } from '$lib/config/languages';

	let {
        class: className = '',
        classButton = 'bg-white text-slate-800 hover:bg-slate-50',
        classDropdown = 'bg-white border-slate-200 text-slate-800',
        classActive = 'bg-blue-50 text-blue-600 font-semibold',
        classInactive = 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
		placement = 'bottom'
    } = $props();

	let currentLocale = $state(getLocale()); 
	let isOpen = $state(false);

	let activeLanguage = $derived(AVAILABLE_LANGUAGES.find((l) => l.code === currentLocale) || AVAILABLE_LANGUAGES[0]);

	async function switchLocale(newLocale: LanguageCode) {
		if (newLocale === currentLocale) {
			isOpen = false;
			return;
		}

        // 1. Persist to backend if logged in and wait for it
        // This avoids race conditions where the page reloads before the backend is updated
        if (authStore.isAuthenticated && authStore.user?.settings.language !== newLocale) {
            await authStore.updateSettings({ language: newLocale });
        }

        // 2. Update local state and cookie
		setLocale(newLocale);
        if (browser) {
            document.cookie = `PARAGLIDE_LOCALE=${newLocale}; path=/; max-age=31536000; SameSite=Lax`;
        }
        currentLocale = newLocale;
        isOpen = false;

		console.log('currentLocale set to:', currentLocale, 'activeLanguage:', activeLanguage.label);

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

    /**
     * Handles clicks outside the component to close the dropdown
     * @param {MouseEvent} event - The click event
     */
	function handleOutsideClick(event: MouseEvent) {
		const target = event.target as HTMLElement;
		if (!target.closest('.lang-switcher-container')) {
			isOpen = false;
		}
	}
</script>

<svelte:window onclick={handleOutsideClick} />
<div class="lang-switcher-container relative flex items-center {className}">
	<button
		type="button"
		onclick={() => (isOpen = !isOpen)}
		class="cursor-pointer inline-flex h-10 items-center justify-center gap-2 border px-3 font-medium transition-all focus:ring-2 focus:ring-blue-500/50 focus:outline-none {classButton}"
		aria-expanded={isOpen}
	>
		<span
			class="flex h-3.5 w-5 flex-shrink-0 items-center justify-center overflow-hidden rounded-xs [&>svg]:h-full [&>svg]:w-full [&>svg]:object-cover"
		>
			{@html activeLanguage.svg}
		</span>

		<span class="mt-[1px] text-xs leading-none font-bold tracking-wider uppercase"
			>{activeLanguage.code}</span
		>

		<ChevronDown
			size={14}
			class="text-slate-400 transition-transform duration-300 
                {isOpen ? 'rotate-180 text-blue-400' : ''}"
		/>
	</button>

	{#if isOpen}
		<div
			transition:fade={{ duration: 150 }}
			class="absolute {placement === 'top' ? 'bottom-full mb-2 origin-bottom-right' : 'top-full mt-2 origin-top-right'} 
                   right-0 z-50 w-32 overflow-hidden border shadow-2xl backdrop-blur-xl focus:outline-none {classDropdown}"
			role="menu"
		>
			<div class="py-1">
				{#each AVAILABLE_LANGUAGES as { code, label, svg }}
					<button
						onclick={() => switchLocale(code)}
						class="cursor-pointer flex h-10 w-full items-center px-3 text-left text-sm transition-colors
                            {currentLocale === code ? classActive : classInactive}"
						role="menuitem"
					>
						<span
							class="mr-2.5 flex h-3.5 w-5 flex-shrink-0 items-center justify-center overflow-hidden rounded-xs shadow-sm [&>svg]:h-full [&>svg]:w-full [&>svg]:object-cover"
						>
							{@html svg}
						</span>
						<span class="truncate">{label}</span>
					</button>
				{/each}
			</div>
		</div>
	{/if}
</div>
