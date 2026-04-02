<script lang="ts">
    import { themeState, THEMES, type ThemeId } from '$lib/themes/themes.svelte';
    import { fade } from 'svelte/transition';
    import { ChevronDown } from 'lucide-svelte';

    let { 
        class: className = '',
        classButton = 'bg-surface border border-border text-copy-secondary hover:text-copy-primary hover:bg-panel',
        classDropdown = 'bg-panel border border-border shadow-xl',
        classActive = 'text-accent bg-surface',
        classInactive = 'text-copy-secondary hover:text-copy-primary hover:bg-surface',
        placement = 'bottom' 
    } = $props();

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

<div class="theme-selector relative flex items-center {className}">
    <button
        type="button"
        aria-expanded={isOpen}
        onclick={() => isOpen = !isOpen}
        class="cursor-pointer flex w-full items-center justify-between gap-2 px-3 h-10 rounded-lg text-sm font-medium transition-all focus:outline-none min-w-0 {classButton}"
    >
        <div class="flex items-center gap-2 min-w-0">
            <span class="flex-shrink-0 flex items-center justify-center 
                        {current.id === 'astronomical' ? 'text-red-500' : 'text-copy-muted'}">
                <current.icon size={16} strokeWidth={2} />
            </span>
            <span class="truncate pt-0.5">{current.label}</span>
        </div>
        
        <ChevronDown
            size={14}
            class="flex-shrink-0 transition-transform duration-300 
                {isOpen ? 'rotate-180 text-accent' : 'text-copy-muted'}"
        />
    </button>

    {#if isOpen}
        <div
            transition:fade={{ duration: 150 }}
            class="absolute {placement === 'top' ? 'bottom-full mb-2 origin-bottom-left' : 'top-full mt-2 origin-top-left'} 
                   left-0 z-50 w-44 overflow-hidden rounded-xl focus:outline-none {classDropdown}"
            role="menu"
        >
            <div class="py-1">
                {#each THEMES as t}
                    <button
                        onclick={() => select(t.id)}
                        class="cursor-pointer flex w-full h-10 items-center gap-3 px-3 text-left text-sm transition-colors
                               {themeState.current === t.id ? classActive : classInactive}"
                        role="menuitem"
                    >
                        <span class="flex-shrink-0 flex items-center justify-center 
                                    {t.id === 'astronomical' ? 'text-red-500' : 'text-copy-muted'}">
                            <t.icon size={16} strokeWidth={2} />
                        </span>
                        <span class="truncate">{t.label}</span>
                    </button>
                {/each}
            </div>
        </div>
    {/if}
</div>