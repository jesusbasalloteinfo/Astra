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

<!-- src/lib/components/observation/sideDockComponents/ThemeDockButton.svelte -->
<script lang="ts">
    import { themeState, THEMES } from '$lib/themes/themes.svelte';
    import { Palette } from 'lucide-svelte';
    import DockPopover from './DockPopover.svelte';
	import { m } from '$lib/paraglide/messages';

    /**
     * Component props
     * @type {{ isOpen: boolean, allowHover?: boolean }}
     * @property {boolean} isOpen - Whether the theme selection popover is open (bindable)
     * @property {boolean} [allowHover=true] - Whether to allow opening the popover on hover
     */
    let { isOpen = $bindable(false), allowHover = true } = $props();

</script>

<DockPopover 
    icon={Palette} 
    title={m.obs_sidedock_theme()}
    buttonTitle={m.obs_sidedock_theme()}
    bind:isOpen
    {allowHover}
>
    <div class="grid grid-cols-2 gap-2">
        {#each THEMES as t}
            <button onclick={() => themeState.set(t.id)}
                class="cursor-pointer flex flex-col items-center justify-center gap-1.5 p-2 rounded-xl transition-all border 
                        {themeState.current === t.id 
                        ? 'bg-accent/20 border-accent/50 text-accent shadow-inner' 
                        : 'bg-panel/40 border-transparent text-copy-muted hover:bg-panel/60 hover:text-copy-primary'}">
                <t.icon size={18} strokeWidth={themeState.current === t.id ? 2.5 : 2} 
                        class={t.id === 'astronomical' && themeState.current === t.id ? 'text-red-500' : ''}/>
                <span class="text-[10px] font-medium leading-none">{t.label}</span>
            </button>
        {/each}
    </div>
</DockPopover>