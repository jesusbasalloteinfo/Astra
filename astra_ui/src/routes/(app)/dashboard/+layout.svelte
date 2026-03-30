<script lang="ts">
    import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
    import ThemeSelector from '$lib/themes/ThemeSelector.svelte';
    let { children } = $props();
</script>

<div class="min-h-screen flex flex-col bg-primary text-copy-primary transition-colors duration-100">
    
    <nav class="px-6 py-3 flex items-center justify-end gap-3 border-b border-border">
        <ThemeSelector />
        <LanguageSwitcher
            classButton="bg-surface border border-border text-copy-secondary hover:text-copy-primary hover:bg-panel rounded-lg"
            classDropdown="bg-panel border  border-border rounded-xl"
            classActive="bg-surface text-accent font-semibold"
            classInactive="text-copy-secondary hover:bg-surface hover:text-copy-primary" />
    </nav>

    <main class="flex-1">
        {@render children()}
    </main>
</div>