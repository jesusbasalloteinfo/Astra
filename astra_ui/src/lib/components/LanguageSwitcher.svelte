<script lang="ts">
    import { getLocale, setLocale } from '$lib/paraglide/runtime.js';
    import { page } from '$app/state';

    let { class: className = "" } = $props();
    let currentLocale = $derived(getLocale());
    let isOpen = $state(false); // State to control if the menu is opened or not

    const LANGUAGES = [ 
        { code: 'en', label: 'English', flag: '🇺🇸' },
        { code: 'es', label: 'Español', flag: '🇪🇸' }
    ] as const;
    
    let activeLanguage = $derived(LANGUAGES.find(l => l.code === currentLocale) || LANGUAGES[0]); // Language to be shown
    function switchLocale(newLocale: 'en' | 'es') {
        if (newLocale === currentLocale) {
            isOpen = false; // Close
            return;
        }

        // Put cookie
        setLocale(newLocale);
        
        const segments = page.url.pathname.split('/');
        
        // Check if is a url-enabled language
        if (segments[1] === 'en' || segments[1] === 'es') {
            segments[1] = newLocale;
            const newPath = segments.join('/') + page.url.search;
            window.location.replace(newPath);
        } else {
            // Not a url, so reload as usual
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

<div class="relative inline-block text-left lang-switcher-container {className}">
    
    <button 
        type="button"
        onclick={() => isOpen = !isOpen}
        class="inline-flex items-center justify-between min-w-[140px] px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
        aria-expanded={isOpen}
    >
        <span class="flex items-center gap-2">
            <span class="text-lg">{activeLanguage.flag}</span>
            <span>{activeLanguage.label}</span>
        </span>
        <svg 
            class="w-4 h-4 ml-2 -mr-1 text-slate-400 transition-transform duration-200 {isOpen ? 'rotate-180' : ''}" 
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 20 20" 
            fill="currentColor"
        >
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
    </button>

    {#if isOpen}
        <div 
            class="absolute right-0 z-50 w-full mt-2 origin-top-right bg-white border border-slate-200 rounded-lg shadow-lg ring-1 ring-black/5 focus:outline-none overflow-hidden"
            role="menu"
        >
            <div class="py-1">
                {#each LANGUAGES as { code, label, flag }}
                    <button
                        onclick={() => switchLocale(code)}
                        class="flex items-center w-full px-4 py-2 text-sm text-left transition-colors
                            {currentLocale === code 
                                ? 'bg-indigo-50 text-indigo-700 font-semibold' 
                                : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'}"
                        role="menuitem"
                    >
                        <span class="mr-3 text-lg">{flag}</span>
                        {label}
                    </button>
                {/each}
            </div>
        </div>
    {/if}

</div>