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

<!-- src/lib/components/observation/sideDockComponents/CommandPaletteShell.svelte -->
<script lang="ts">
    import { fade } from 'svelte/transition';
    import { m } from '$lib/paraglide/messages';

    let { 
        open = $bindable(false), 
        children,
        maxWidth = 'max-w-2xl'
    } = $props();

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            open = false;
        }
    }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
    <div transition:fade={{ duration: 150 }} class="absolute inset-0 z-50 flex items-start justify-center pt-16 md:pt-32 px-4 md:px-0 pointer-events-auto">
        <button 
            class="absolute inset-0 w-full h-full bg-black/60 backdrop-blur-sm cursor-default appearance-none border-none focus:outline-none" 
            onclick={() => open = false} 
            aria-label={m.obs_skyfinder_close()} 
            tabindex="-1"
        ></button>

        <div class="relative z-10 w-full {maxWidth} max-h-[80vh] md:max-h-[60vh] bg-surface backdrop-blur-xl border border-border rounded-2xl md:rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden flex flex-col">
            {@render children()}
        </div>
    </div>
{/if}