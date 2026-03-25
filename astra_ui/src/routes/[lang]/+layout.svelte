<script lang="ts">
    import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
    import { page } from '$app/state';
    import { setLocale } from '$lib/paraglide/runtime.js';

    let { children } = $props();

    // Sync Paraglide with URL
    $effect.pre(() => {
        const urlLang = page.params.lang; // Get the param
        
        if (urlLang === 'es' || urlLang === 'en') {
            setLocale(urlLang);
        }
    });
</script>

<nav class="p-4 flex justify-end">
    <LanguageSwitcher />
</nav>

{@render children()}