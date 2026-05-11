<!-- src/lib/components/observation/sideDockComponents/ConfigEntry.svelte -->
<script lang="ts">
    import { ChevronDown, ChevronUp } from 'lucide-svelte';
    import { slide } from 'svelte/transition';
    import type { Snippet } from 'svelte';

    let { 
        icon: IconComponent, 
        label = '', 
        active = false, 
        disabled = false,
        onToggle,
        submenuOpen = false,
        onToggleSubmenu = () => {},
        children 
    }: {
        icon?: any,
        label?: string,
        active?: boolean,
        disabled?: boolean,
        onToggle: () => void,
        submenuOpen?: boolean,
        onToggleSubmenu?: () => void,
        children?: Snippet
    } = $props();

    const hasSubmenu = $derived(!!children);
</script>

<div class="flex flex-col w-full">
    <div class="flex items-center justify-between w-full">
        <!-- Main Toggle Button -->
        <button 
            onclick={onToggle}
            disabled={disabled}
            class="cursor-pointer flex items-center gap-2 px-2 py-1.5 rounded hover:bg-panel/40 text-xs flex-1 transition-all
                   {active && !disabled ? 'text-accent' : 'text-copy-muted'}
                   {disabled ? 'opacity-40 cursor-not-allowed' : ''}"
        >
            {#if IconComponent}
                <IconComponent size={14}/>
            {/if}
            <span>{label}</span>
        </button>
        
        <!-- Optional Submenu Toggle -->
        {#if hasSubmenu && active && !disabled}
            <button 
                onclick={onToggleSubmenu} 
                class="p-1.5 text-copy-muted hover:text-white hover:bg-panel/40 rounded transition-all ml-1 cursor-pointer"
            >
                {#if submenuOpen}
                    <ChevronUp size={14}/>
                {:else}
                    <ChevronDown size={14}/>
                {/if}
            </button>
        {/if}
    </div>

    <!-- Submenu Content -->
    {#if hasSubmenu && active && !disabled && submenuOpen && children}
        <div transition:slide={{ duration: 200 }} class="flex flex-col ml-4 border-l border-border/50 pl-1 my-1 overflow-hidden">
            {@render children()}
        </div>
    {/if}
</div>