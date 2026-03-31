<script lang="ts">
    import { page } from '$app/state';
    import { setLocale } from '$lib/paraglide/runtime.js';
    import { AVAILABLE_LANGUAGES, type LanguageCode } from '$lib/config/languages';

    let { children } = $props();

    // Sync Paraglide with URL
    $effect.pre(() => {

        const urlLang = page.params.lang as string; // Get the param
        
        const validLocales = AVAILABLE_LANGUAGES.map(l => l.code);
        
        if (validLocales.includes(urlLang as LanguageCode)) {
            setLocale(urlLang as LanguageCode);
        }
    });
</script>



{@render children()}

