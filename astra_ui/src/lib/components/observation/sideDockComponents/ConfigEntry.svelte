<!--
  ASTRA - Automated Smart Telescope Remote Assistant
  Copyright (C) 2026 Jesus Basallote
  
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.
  
  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<!-- src/lib/components/observation/sideDockComponents/ConfigEntry.svelte -->
<script lang="ts">
    import { ChevronDown, ChevronUp } from 'lucide-svelte';
    import { slide } from 'svelte/transition';
    import type { Snippet } from 'svelte';

    /**
     * Component props
     * @type {{ icon?: any, label?: string, active?: boolean, disabled?: boolean, onToggle: () => void, submenuOpen?: boolean, onToggleSubmenu?: () => void, children?: Snippet }}
     * @property {any} [icon] - Optional icon component to display
     * @property {string} [label=''] - Text label for the entry
     * @property {boolean} [active=false] - Whether the entry is currently active
     * @property {boolean} [disabled=false] - Whether the entry is disabled
     * @property {() => void} onToggle - Function called when the main button is clicked
     * @property {boolean} [submenuOpen=false] - Whether the submenu (if any) is expanded
     * @property {() => void} [onToggleSubmenu] - Function called when the submenu toggle is clicked
     * @property {Snippet} [children] - Optional snippet for submenu content
     */
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

    /** Whether the component has a submenu (determined by the presence of children) */
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