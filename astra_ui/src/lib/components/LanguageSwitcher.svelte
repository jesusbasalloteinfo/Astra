<script lang="ts">
	import { getLocale, setLocale } from '$lib/paraglide/runtime.js';
    import { browser } from '$app/environment';
	import { page } from '$app/state';
	import { fade } from 'svelte/transition';
	import { ChevronDown } from 'lucide-svelte';

	import { AVAILABLE_LANGUAGES, type LanguageCode } from '$lib/config/languages';

	let {
        class: className = '',
        classButton = 'bg-white text-slate-800 hover:bg-slate-50',
        classDropdown = 'bg-white border-slate-200 text-slate-800',
        classActive = 'bg-blue-50 text-blue-600 font-semibold',
        classInactive = 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
    } = $props();

	let currentLocale = $state(getLocale()); 
	let isOpen = $state(false);

	let activeLanguage = $derived(AVAILABLE_LANGUAGES.find((l) => l.code === currentLocale) || AVAILABLE_LANGUAGES[0]);

	function switchLocale(newLocale: LanguageCode) {
		if (newLocale === currentLocale) {
			isOpen = false;
			return;
		}

		setLocale(newLocale);
        currentLocale = newLocale;
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
		class="inline-flex h-10 items-center justify-center gap-2 border px-3 font-medium transition-all focus:ring-2 focus:ring-blue-500/50 focus:outline-none {classButton}"
		aria-expanded={isOpen}
	>
		<span
			class="flex h-3.5 w-5 flex-shrink-0 items-center justify-center overflow-hidden rounded-xs [&>svg]:h-full [&>svg]:w-full [&>svg]:object-cover"
		>
			{#if browser}
                {@html activeLanguage.svg}
            {:else}
                <span class="h-full w-full bg-slate-200 rounded-xs"></span>
            {/if}
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
			class="absolute top-full left-0 origin-top-left md:right-0 md:left-auto md:origin-top-right z-50 mt-2 w-32  overflow-hidden border shadow-2xl backdrop-blur-xl focus:outline-none {classDropdown}"
			role="menu"
		>
			<div class="py-1">
				{#each AVAILABLE_LANGUAGES as { code, label, svg }}
					<button
						onclick={() => switchLocale(code)}
						class="flex h-10 w-full items-center px-3 text-left text-sm transition-colors
                            {currentLocale === code ? classActive : classInactive}"
						role="menuitem"
					>
						<span
							class="mr-2.5 flex h-3.5 w-5 flex-shrink-0 items-center justify-center overflow-hidden rounded-xs shadow-sm [&>svg]:h-full [&>svg]:w-full [&>svg]:object-cover"
						>
							{@html svg}
						</span>
						<span class="leading-none">{label}</span>
					</button>
				{/each}
			</div>
		</div>
	{/if}
</div>
