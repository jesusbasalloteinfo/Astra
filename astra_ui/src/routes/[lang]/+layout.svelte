<!-- src/routes/[lang]/+layout.svelte -->
<script lang="ts">
    import { setLocale } from '$lib/paraglide/runtime.js';
    import { page } from '$app/state';
    let { children } = $props();

    // Sync Paraglide whenever the [lang] param changes
    $effect(() => {
        const lang = page.params.lang as 'en' | 'es';
        setLocale(lang);
    });
</script>

{@render children()}