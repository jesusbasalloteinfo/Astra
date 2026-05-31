<!-- src/lib/components/dashboard/MobileThemeSelector.svelte -->
<script lang="ts">
    import { themeState, THEMES, type ThemeId } from '$lib/themes/themes.svelte';
    import { fade } from 'svelte/transition';

    /**
     * Updates the application theme
     * @param {ThemeId} id - The unique identifier of the selected theme
     */
    function select(id: ThemeId) {
        themeState.set(id);
    }
</script>

<div class="flex flex-col gap-3">
    <span class="text-[10px] font-bold text-copy-muted uppercase tracking-[0.2em] px-1">Theme</span>
    <div class="grid grid-cols-2 gap-2">
        {#each THEMES as t}
            {@const isActive = themeState.current === t.id}
            <button
                onclick={() => select(t.id)}
                class="flex flex-col items-center justify-center gap-2 p-3 rounded-2xl border transition-all active:scale-95
                       {isActive 
                        ? 'bg-accent/10 border-accent text-accent shadow-lg shadow-accent/5' 
                        : 'bg-surface border-border text-copy-secondary'}"
            >
                <div class="p-2 rounded-xl {isActive ? 'bg-accent/10' : 'bg-secondary'}">
                    <t.icon size={20} class={t.id === 'astronomical' && !isActive ? 'text-red-500/70' : ''} />
                </div>
                <span class="text-xs font-bold tracking-tight">{t.label}</span>
            </button>
        {/each}
    </div>
</div>
