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

<!-- src/lib/components/observation/sideDockComponents/DockPopover.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';

    /**
     * Component props
     * @type {{ icon?: any, title?: string, buttonTitle?: string, active?: boolean, activeClass?: string, isOpen: boolean, allowHover?: boolean, children: Snippet }}
     * @property {any} [icon] - Optional icon component for the trigger button
     * @property {string} [title=''] - Title displayed inside the popover
     * @property {string} [buttonTitle=''] - Tooltip title for the trigger button
     * @property {boolean} [active=false] - Whether the button should show active styling
     * @property {string} [activeClass] - CSS classes to apply when active or open
     * @property {boolean} isOpen - Whether the popover is open (bindable)
     * @property {boolean} [allowHover=true] - Whether to allow opening the popover on hover (on supported devices)
     * @property {Snippet} children - Snippet for the popover content
     */
    let { 
        icon: IconComponent, 
        title = '', 
        buttonTitle = '',
        active = false,
        activeClass = 'bg-accent text-white shadow-[0_0_15px_var(--color-accent-glow)]',
        isOpen = $bindable(false),
        allowHover = true,
        children 
    } = $props();

    /** Reference to the container element for outside click detection */
    let container: HTMLElement;

    /**
     * Toggles the open state of the popover
     */
    function toggle() {
        isOpen = !isOpen;
    }

    /**
     * Handles clicks outside the component to close the popover
     * @param {PointerEvent} event - The pointer event
     */
    function handleClickOutside(event: PointerEvent) {
        if (container && !container.contains(event.target as Node)) {
            isOpen = false;
        }
    }

    onMount(() => {
        document.addEventListener('pointerdown', handleClickOutside);
        return () => {
            document.removeEventListener('pointerdown', handleClickOutside);
        };
    });
</script>

<div class="relative group" bind:this={container} class:hover-disabled={!allowHover}>
    <!-- Trigger Button -->
    <button 
        onclick={toggle}
        title={buttonTitle}
        class="flex items-center justify-center cursor-pointer p-3 max-lg:landscape:p-2 rounded-full transition-all shadow-inner 
               {active || isOpen
                ? activeClass 
                : 'hover:bg-panel/50 text-copy-muted hover:text-white'}"
    >
        {#if IconComponent}
            <IconComponent size={20} class="max-lg:landscape:w-4 max-lg:landscape:h-4" />
        {/if}
    </button>

    <!-- Popover Menu -->
    <div class="absolute left-full top-1/2 -translate-y-1/2 pl-4 transition-all z-50 popover-menu
                {isOpen ? 'opacity-100 pointer-events-auto visible' : 'opacity-0 pointer-events-none invisible'}">
        <div class="p-3 bg-surface backdrop-blur-xl border border-border rounded-2xl w-52 shadow-xl flex flex-col gap-2">
            {#if title}
                <span class="text-[10px] font-bold text-accent px-2 pb-1.5 mb-1 border-b border-border/50 uppercase tracking-widest leading-tight">
                    {title}
                </span>
            {/if}
            
            <div class="flex flex-col gap-1">
                {@render children()}
            </div>
        </div>
    </div>
</div>

<style>
    /* Restore hover behavior only for devices that support it (PC) */
    /* Only allow hover if not explicitly disabled */
    @media (hover: hover) {
        .group:not(.hover-disabled):hover .popover-menu {
            opacity: 1;
            visibility: visible;
            pointer-events: auto;
        }
    }
</style>