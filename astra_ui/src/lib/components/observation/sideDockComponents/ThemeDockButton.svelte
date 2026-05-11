<!-- src/lib/components/observation/sideDockComponents/ThemeDockButton.svelte -->
<script lang="ts">
    import { themeState, THEMES } from '$lib/themes/themes.svelte';
    import { Palette } from 'lucide-svelte';
    import DockPopover from './DockPopover.svelte';
	import { m } from '$lib/paraglide/messages';

</script>

<DockPopover 
    icon={Palette} 
    title={m.obs_sidedock_theme()}
    buttonTitle={m.obs_sidedock_theme()}
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