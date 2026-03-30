<script lang="ts">
    import { themeState, THEMES, type ThemeId } from '$lib/themes/themes.svelte';
    import { fade } from 'svelte/transition';

    let { class: className = '' } = $props();

    let isOpen = $state(false);
    let current = $derived(THEMES.find(t => t.id === themeState.current) ?? THEMES[0]);

    function select(id: ThemeId) {
        themeState.set(id);
        isOpen = false;
    }

    function handleOutside(e: MouseEvent) {
        if (!(e.target as HTMLElement).closest('.theme-selector')) isOpen = false;
    }
</script>

<svelte:window onclick={handleOutside} />

<div class="theme-selector relative {className}">
    <button
        onclick={() => isOpen = !isOpen}
        class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all
               bg-surface border border-border text-copy-secondary hover:text-copy-primary hover:bg-panel">
        <span>{current.icon}</span>
        <span>{current.label}</span>
    </button>

    {#if isOpen}
        <div
            transition:fade={{ duration: 120 }}
            class="absolute right-0 top-full mt-2 w-44 rounded-xl border border-border bg-panel shadow-xl z-50 overflow-hidden">
            {#each THEMES as t}
                <button
                    onclick={() => select(t.id)}
                    class="flex items-center gap-3 w-full px-4 py-2.5 text-sm transition-colors
                           {themeState.current === t.id
                               ? 'text-accent bg-surface'
                               : 'text-copy-secondary hover:text-copy-primary hover:bg-surface'}">
                    <span>{t.icon}</span>
                    <span>{t.label}</span>
                </button>
            {/each}
        </div>
    {/if}
</div>